import hashlib
import io
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import Mock, patch

from week2.parse_query import empty_filters, parse_property_query
from week2.test_queries import CASES
from week3 import db, search, sold
from week3.format import format_cards, number_text
from week4.conversation import handle_turn
from week4.session import get_session, update_session, clear_session

ROOT = Path(__file__).resolve().parents[1]


class ParserTests(unittest.TestCase):
    def test_original_ten_queries(self):
        for text, changes in CASES:
            with self.subTest(query=text):
                self.assertEqual(parse_property_query(text), {**empty_filters(), **changes})

    def test_cli_and_empty_input(self):
        result = subprocess.run([sys.executable, "week2/cli.py", "Condos in Irvine under $900k"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["maxPrice"], 900000)
        result = subprocess.run([sys.executable, "week2/cli.py"], cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


class DatabaseTests(unittest.TestCase):
    """Execute the generated SELECT statements on synthetic rows using SQLite.

    This checks filtering/pagination without claiming a live MySQL test.
    """
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.create_function("REGEXP", 2, lambda p, v: bool(v and re.search(p, v)))
        self.connection.executescript("""
            CREATE TABLE rets_property (
              id INTEGER, L_ListingID TEXT, L_Address TEXT, L_City TEXT, L_Zip TEXT,
              L_SystemPrice INTEGER, L_Keyword2 INTEGER, LM_Dec_3 REAL, LM_Int2_3 INTEGER,
              L_Type_ TEXT, L_Status TEXT, PhotoCount INTEGER, AssociationFee INTEGER,
              PoolPrivateYN TEXT, ViewYN TEXT);
            CREATE TABLE california_sold (
              ListingKey INTEGER, UnparsedAddress TEXT, City TEXT, CloseDate TEXT,
              ClosePrice REAL, BedroomsTotal INTEGER, BathroomsTotalInteger INTEGER,
              LivingArea REAL, PropertySubType TEXT, DaysOnMarket INTEGER, PropertyType TEXT);
        """)
        for i, pool in enumerate(("1", "0", "", None, "True", "False"), 1):
            self.connection.execute("INSERT INTO rets_property VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (i, str(i), f"Test address {i}", "Irvine", "00000", 400000 + i * 1000,
                 3, 2.5, 1800, "Condominium", "Active", 10, 300, pool, "1"))
        self.connection.execute("INSERT INTO rets_property SELECT 7, '7', 'Other city', 'Pasadena', '00000', 100000, 3, 2, 1800, 'Condominium', 'Active', 5, 0, '1', '1'")
        for key, close_date, price in ((1, "2026-09-17", 500000), (2, "2072-06-29", 800000),
                                       (3, "2025-01-01", 900000), (4, "2026-09-18", 0),
                                       (5, "bad-date", 500000), (6, "2026-10-13", 600000)):
            self.connection.execute("INSERT INTO california_sold VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (key, "Synthetic sold address", "Irvine", close_date, price, 3, 2, 1800,
                 "Condominium", 10, "Residential"))
        self.active_patch = patch.object(search, "query", self.execute)
        self.sold_patch = patch.object(sold, "query", self.execute)
        self.active_patch.start()
        self.sold_patch.start()

    def tearDown(self):
        self.active_patch.stop()
        self.sold_patch.stop()
        self.connection.close()

    def execute(self, sql, params):
        return [dict(row) for row in self.connection.execute(sql.replace("%s", "?"), params).fetchall()]

    def test_active_filters_and_pagination(self):
        filters = parse_property_query("3 bed condos in Irvine under $900k with HOA under $500")
        first = search.search_active_listings(filters, 1, 3)
        second = search.search_active_listings(filters, 2, 3)
        self.assertTrue(first["hasMore"])
        self.assertFalse(second["hasMore"])
        self.assertEqual(len(first["properties"]), 3)
        self.assertTrue(set(p["id"] for p in first["properties"]).isdisjoint(p["id"] for p in second["properties"]))
        for row in first["properties"] + second["properties"]:
            self.assertEqual(row["city"], "Irvine")
            self.assertLessEqual(row["price"], 900000)
            self.assertGreaterEqual(row["beds"], 3)
            self.assertEqual(row["photoCount"], 10)

    def test_feature_unknowns_are_not_false(self):
        for value, expected in (("True", {1, 5}), ("False", {2, 6})):
            filters = {**empty_filters(), "city": "Irvine", "pool": value}
            rows = search.search_active_listings(filters, limit=50)["properties"]
            self.assertEqual({row["id"] for row in rows}, expected)

    def test_no_match_and_injection(self):
        self.assertEqual(search.search_active_listings(parse_property_query("Condos in Irvine under $1"))["properties"], [])
        payload = "Irvine' OR 1=1 --"
        filters = {**empty_filters(), "city": payload}
        sql, params = search.build_active_query(filters)
        self.assertNotIn(payload, sql)
        self.assertIn(payload, params)
        self.assertEqual(search.search_active_listings(filters)["properties"], [])

    def test_invalid_pagination_and_numbers(self):
        for page, limit in ((0, 5), (True, 5), (1.5, 5), (1, 51), (1, 0)):
            with self.subTest(page=page, limit=limit), self.assertRaises(ValueError):
                search.search_active_listings(empty_filters(), page, limit)
        for value in (-1, float("inf"), float("nan"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                search.search_active_listings({**empty_filters(), "maxPrice": value})

    def test_recent_sold_excludes_future_old_and_zero(self):
        result = sold.get_sold_comps("Irvine", as_of="2026-10-13")
        self.assertEqual([row["listingId"] for row in result["properties"]], ["6", "1"])
        self.assertEqual(result["asOf"], "2026-10-13")

    def test_sold_month_end_and_validation(self):
        sql, params, _ = sold.build_sold_query("Irvine", months=1, as_of="2024-03-31")
        self.assertEqual(params[2], "2024-02-29")
        self.assertIn("LIMIT %s OFFSET %s", sql)
        for kwargs in ({"months": 0}, {"as_of": "2026-02-30"}, {"as_of": "2026-2-3"}, {"city": ""}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                sold.build_sold_query(**{"city": "Irvine", **kwargs})

    def test_formatter_and_decimal_json(self):
        row = search.search_active_listings(empty_filters())["properties"][0]
        card = format_cards([row])
        self.assertIn("Photos:", card)
        self.assertIn("Beds: 3", card)
        self.assertEqual(number_text(Decimal("2.5")), "2.5")
        self.assertEqual(number_text(None), "Unknown")
        self.assertEqual(number_text(0), "0")
        self.assertEqual(number_text(1128888, True), "$1,128,888")
        self.assertEqual(format_cards([]), "No matching properties found.")
        self.assertEqual(json.loads(db.json_text({"price": Decimal("2.5")})), {"price": 2.5})

    def test_connector_closes_on_success_and_failure(self):
        connection, cursor = Mock(), Mock()
        connection.cursor.return_value = cursor
        cursor.fetchall.return_value = [{"value": 1}]
        with patch.object(db, "connect", return_value=connection):
            self.assertEqual(db.query("SELECT %s", [1]), [{"value": 1}])
        cursor.execute.assert_called_once_with("SELECT %s", (1,))
        cursor.close.assert_called_once()
        connection.close.assert_called_once()
        cursor.reset_mock()
        connection.reset_mock()
        cursor.execute.side_effect = RuntimeError("test failure")
        with patch.object(db, "connect", return_value=connection), self.assertRaises(RuntimeError):
            db.query("SELECT %s", [1])
        cursor.close.assert_called_once()
        connection.close.assert_called_once()

    def test_week4_cli_questions_and_cards(self):
        from week4.cli import main
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"IDX_SESSION_DIR": directory}):
            for message in ("Start over", "Find homes in Irvine", "Under $900k", "Condos with 3 beds"):
                output = io.StringIO()
                with patch.object(sys, "argv", ["cli.py", "cli-test", message]), patch("sys.stdout", output):
                    self.assertEqual(main(), 0)
            self.assertIn("Photos: 10", output.getvalue())
            self.assertIn('"city": "Irvine"', output.getvalue())
            self.assertIn("Source: imported MLS dataset", output.getvalue())


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"IDX_SESSION_DIR": self.directory.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.directory.cleanup()

    def test_full_conversation_refine_and_reset(self):
        self.assertFalse(handle_turn("a", "Start over")["ready"])
        self.assertIn("budget", handle_turn("a", "Find homes in Irvine")["question"])
        self.assertIn("Condo", handle_turn("a", "Under $1.2M")["question"])
        turn = handle_turn("a", "Single family with at least 3 beds")
        self.assertTrue(turn["ready"])
        changed = handle_turn("a", "Under $1.5M")["filters"]
        self.assertEqual(changed["city"], "Irvine")
        self.assertEqual(changed["maxPrice"], 1500000)
        self.assertEqual(changed["beds"], 3)
        self.assertEqual(changed["type"], "SingleFamilyResidence")
        self.assertEqual(handle_turn("a", "reset")["filters"], empty_filters())

    def test_any_type_and_separate_sessions(self):
        handle_turn("a", "Homes in Irvine under $900k")
        self.assertTrue(handle_turn("a", "any type")["ready"])
        self.assertIsNone(get_session("a")["filters"]["type"])
        self.assertIsNone(get_session("b")["filters"]["city"])

    def test_persistence_across_processes(self):
        for action in ("save", "refine", "show"):
            result = subprocess.run([sys.executable, "week4/session_demo.py", action], cwd=ROOT,
                                    capture_output=True, text=True, env=os.environ.copy())
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["filters"]["beds"], 3)
        self.assertEqual(json.loads(result.stdout)["filters"]["city"], "Irvine")

    def test_existing_typescript_session_and_null_clear(self):
        path = Path(self.directory.name) / (hashlib.sha256(b"old").hexdigest() + ".json")
        path.write_text(json.dumps(dict(filters={**empty_filters(), "city": "Irvine", "type": "Condominium"}, page=1, updatedAt="2026-10-13T00:00:00Z")))
        self.assertEqual(get_session("old")["filters"]["city"], "Irvine")
        update_session("old", {"type": None})
        self.assertIsNone(get_session("old")["filters"]["type"])
        self.assertTrue(get_session("old")["typePreferenceAnswered"])

    def test_empty_message_invalid_session_and_unknown_fields(self):
        with self.assertRaises(ValueError):
            handle_turn("a", " ")
        with self.assertRaises(ValueError):
            get_session("")
        with self.assertRaises(ValueError):
            update_session("a", {"notAFilter": 1})


if __name__ == "__main__":
    unittest.main()
