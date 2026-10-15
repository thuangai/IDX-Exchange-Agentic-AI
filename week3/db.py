"""Load settings only when a database call is made; never print credentials."""
import json
import os
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def connect():
    import mysql.connector
    from dotenv import load_dotenv

    explicit = os.environ.get("IDX_ENV_FILE")
    if explicit:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError("IDX_ENV_FILE does not point to an existing file.")
        load_dotenv(path)
    else:
        for path in (ROOT / "week3" / ".env", ROOT / ".env"):
            if path.is_file():
                load_dotenv(path)
                break

    for key in ("MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DATABASE"):
        if not os.environ.get(key):
            raise ValueError(f"Missing setting: {key}")
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
        connection_timeout=10,
    )


def query(sql: str, params=()):
    """Bind values with the connector's %s placeholders, never string formatting."""
    connection = connect()
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def json_text(value):
    def convert(item):
        if isinstance(item, Decimal):
            return int(item) if item == item.to_integral_value() else float(item)
        if isinstance(item, (date, datetime)):
            return item.isoformat()
        raise TypeError(f"Cannot serialize {type(item).__name__}")
    return json.dumps(value, indent=2, default=convert)
