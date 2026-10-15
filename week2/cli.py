"""Run: python week2/cli.py "Condos in Irvine under $900k"."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import parse_property_query


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        print("Please provide a property-search query.", file=sys.stderr)
        return 1
    print(json.dumps(parse_property_query(query), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
