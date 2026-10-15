import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week3.db import query, json_text


def main():
    try:
        rows = query("""SELECT DATABASE() AS database_name,
            (SELECT COUNT(*) FROM rets_property) AS active_listings,
            (SELECT COUNT(*) FROM california_sold) AS sold_properties""")
        print(json_text(rows))
        print("MySQL connection successful!")
        return 0
    except Exception as error:
        print(f"Connection failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
