import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import parse_property_query
from week3.search import search_active_listings
from week3.sold import get_sold_comps
from week3.format import format_cards


def main():
    parser = argparse.ArgumentParser(description="Search the imported MLS dataset.")
    parser.add_argument("mode", choices=("active", "sold"))
    parser.add_argument("text", help="Search query for active; city for sold")
    parser.add_argument("page", nargs="?", type=int, default=1)
    parser.add_argument("limit", nargs="?", type=int, default=5)
    parser.add_argument("months", nargs="?", type=int, default=12)
    args = parser.parse_args()
    try:
        if args.mode == "active":
            result = search_active_listings(parse_property_query(args.text), args.page, args.limit)
        else:
            result = get_sold_comps(args.text, args.months, args.page, args.limit)
        print(f"Source: imported MLS dataset | Page {result['page']}")
        if "asOf" in result:
            print(f"Sales window: {result['months']} months through {result['asOf']}")
        print("\n" + format_cards(result["properties"], args.mode))
        print(f"\nMore results available: {str(result['hasMore']).lower()}")
        return 0
    except Exception as error:
        print(f"Search failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
