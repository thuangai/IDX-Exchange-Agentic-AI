import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import parse_property_query

if __name__ == "__main__":
    print(json.dumps(parse_property_query(
        "Show me 3-bedroom condos in Irvine under $1.5M with a pool."
    ), indent=2))
