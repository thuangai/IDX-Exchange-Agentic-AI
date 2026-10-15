"""Plain-text property cards for the terminal and WhatsApp."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def number_text(value, currency=False):
    if value is None or value == "":
        return "Unknown"
    try:
        number = Decimal(str(value))
        if not number.is_finite():
            return "Unknown"
        if currency:
            return f"${number.quantize(Decimal('1'), rounding=ROUND_HALF_UP):,}"
        return format(number, ",f").rstrip("0").rstrip(".") if number % 1 else f"{int(number):,}"
    except (InvalidOperation, ValueError):
        return "Unknown"


def format_cards(properties, mode="active"):
    if mode not in ("active", "sold"):
        raise ValueError("Mode must be active or sold.")
    if not properties:
        return "No matching properties found."
    cards = []
    for index, prop in enumerate(properties, 1):
        lines = [
            f"{index}. {prop.get('address') or 'Address unavailable'}, {prop.get('city') or 'City unavailable'}",
            f"{'Sold price' if mode == 'sold' else 'List price'}: {number_text(prop.get('price'), True)}",
            f"Beds: {number_text(prop.get('beds'))} | Baths: {number_text(prop.get('baths'))} | Sqft: {number_text(prop.get('sqft'))}",
            f"Type: {prop.get('type') or 'Unknown'}",
            f"Listing ID: {prop.get('listingId') if prop.get('listingId') is not None else 'Unknown'}",
        ]
        if mode == "sold":
            lines.append(f"Closed: {prop.get('closeDate') or 'Unknown'}")
        else:
            lines.extend((f"HOA fee: {number_text(prop.get('hoa'), True)}",
                          f"Photos: {number_text(prop.get('photoCount'))}"))
        cards.append("\n".join(lines))
    return "\n\n".join(cards)
