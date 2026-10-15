import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import parse_property_query
from week3.search import search_active_listings
from week3.db import json_text

if __name__ == "__main__":
    try:
        text = " ".join(sys.argv[1:]).strip()
        if not text:
            raise ValueError("Please provide a property search.")
        filters = parse_property_query(text)
        print(json_text({"filters": filters, **search_active_listings(filters)}))
    except Exception as error:
        print(f"Search failed: {error}", file=sys.stderr)
        raise SystemExit(1)
