import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week3.sold import get_sold_comps
from week3.db import json_text

if __name__ == "__main__":
    try:
        city = sys.argv[1] if len(sys.argv) > 1 else "Irvine"
        months = int(sys.argv[2]) if len(sys.argv) > 2 else 12
        print(json_text(get_sold_comps(city, months)))
    except Exception as error:
        print(f"Sold search failed: {error}", file=sys.stderr)
        raise SystemExit(1)
