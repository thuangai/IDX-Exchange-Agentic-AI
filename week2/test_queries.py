"""The same ten test cases as the TypeScript version."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import empty_filters, parse_property_query

CASES = [
    ("Show me 3-bedroom condos in Irvine under $1.5M with a pool.",
     {"city": "Irvine", "maxPrice": 1500000, "beds": 3, "type": "Condominium", "pool": "True"}),
    ("Townhomes in Newport Beach under $900k",
     {"city": "Newport Beach", "maxPrice": 900000, "type": "Townhouse"}),
    ("Single-family homes in Pasadena with 4 beds and 2.5 baths",
     {"city": "Pasadena", "beds": 4, "baths": 2.5, "type": "SingleFamilyResidence"}),
    ("Land in Riverside under $250,000",
     {"city": "Riverside", "maxPrice": 250000, "type": "UnimprovedLand"}),
    ("Homes with 1,800 square feet", {"sqft": 1800}),
    ("Condos with HOA under $500", {"type": "Condominium", "maxHOA": 500}),
    ("Homes without a pool", {"pool": "False"}),
    ("Homes with a view", {"hasView": "True"}),
    ("Homes with no view and 2 bedrooms", {"hasView": "False", "beds": 2}),
    ("Show me homes", {}),
]


def main():
    failed = 0
    for index, (query, changes) in enumerate(CASES, 1):
        expected = {**empty_filters(), **changes}
        actual = parse_property_query(query)
        if actual == expected:
            print(f"PASS {index}: {query}")
        else:
            failed += 1
            print(f"FAIL {index}: {query}\nExpected: {expected}\nActual: {actual}")
    print(f"\n{len(CASES) - failed}/{len(CASES)} passed")
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
