import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week4.conversation import handle_turn
from week3.search import search_active_listings
from week3.format import format_cards
from week3.db import json_text


def main():
    parser = argparse.ArgumentParser(description="One property-search conversation turn.")
    parser.add_argument("session_id", help="Trusted conversation ID; demo for local testing only")
    parser.add_argument("message", nargs="+")
    args = parser.parse_args()
    try:
        turn = handle_turn(args.session_id, " ".join(args.message))
        if not turn["ready"]:
            print(turn["question"])
            return 0
        result = search_active_listings(turn["filters"], 1, 5)
        print("Searching with these saved preferences:")
        print(json_text(turn["filters"]))
        print("\nSource: imported MLS dataset\n")
        print(format_cards(result["properties"], "active"))
        print(f"\nMore results available: {str(result['hasMore']).lower()}")
        print("You can change your preferences or say 'start over'.")
        return 0
    except Exception as error:
        print(f"Conversation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
