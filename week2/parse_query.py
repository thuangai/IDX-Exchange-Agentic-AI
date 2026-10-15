"""The original Week 2 regular-expression parser, rewritten in Python."""
import re


def empty_filters():
    return dict.fromkeys((
        "city", "maxPrice", "beds", "baths", "sqft", "type",
        "pool", "hasView", "maxHOA",
    ))


def parse_property_query(query: str) -> dict:
    """Extract supported phrases. Missing preferences are None (JSON null)."""
    def match(pattern, text=query):
        return re.search(pattern, text, re.IGNORECASE)

    def number(text):
        value = float(text.replace(",", ""))
        return int(value) if value.is_integer() else value

    city = match(r"\bin\s+([a-z]+(?:\s+[a-z]+)*?)(?=\s+(?:under|with|at|over|for|and)\b|[,.!?]|$)")
    price_query = re.sub(
        r"\bHOA\s+(?:under|below)\s+\$?[\d,]+(?:\.\d+)?\s*[km]?\b",
        "", query, flags=re.IGNORECASE,
    )
    price = match(r"\bunder\s+\$?([\d,]+(?:\.\d+)?)\s*([km])?\b", price_query)
    beds = match(r"\b(\d+)[ -]*(?:bedrooms?|beds?)\b")
    baths = match(r"\b(\d+(?:\.\d+)?)[ -]*(?:bathrooms?|baths?)\b")
    sqft = match(r"\b([\d,]+)\s*(?:sqft|sq ft|square feet)\b")
    hoa = match(r"\bHOA\s+(?:under|below)\s+\$?([\d,]+)\b")

    property_type = None
    for pattern, label in [
        (r"\bcondos?\b|\bcondominiums?\b", "Condominium"),
        (r"\btownhomes?\b|\btownhouses?\b", "Townhouse"),
        (r"\bsingle[ -]family\b", "SingleFamilyResidence"),
        (r"\bland\b", "UnimprovedLand"),
    ]:
        if match(pattern):
            property_type = label
            break

    def feature(name):
        if match(rf"\b(?:no|without)\s+(?:a\s+)?{name}\b"):
            return "False"
        return "True" if match(rf"\b{name}\b") else None

    max_price = None
    if price:
        multiplier = {"m": 1_000_000, "k": 1_000}.get((price[2] or "").lower(), 1)
        max_price = number(price[1]) * multiplier

    return {
        "city": city[1].strip() if city else None,
        "maxPrice": max_price,
        "beds": number(beds[1]) if beds else None,
        "baths": number(baths[1]) if baths else None,
        "sqft": number(sqft[1]) if sqft else None,
        "type": property_type,
        "pool": feature("pool"),
        "hasView": feature("view"),
        "maxHOA": number(hoa[1]) if hoa else None,
    }
