"""Recent residential sales. These are city/date candidates, not valuations."""
import calendar
import re
from datetime import date, datetime, timezone
from week3.db import query
from week3.search import pagination


def build_sold_query(city, months=12, page=1, limit=5, as_of=None):
    if not isinstance(city, str) or not city.strip():
        raise ValueError("Please provide a city.")
    if type(months) is not int or not 1 <= months <= 120:
        raise ValueError("Months must be between 1 and 120.")
    offset = pagination(page, limit)
    as_of = as_of or datetime.now(timezone.utc).date().isoformat()
    if not isinstance(as_of, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
        raise ValueError("as_of must be a valid YYYY-MM-DD date.")
    end = date.fromisoformat(as_of)
    # Match MySQL DATE_SUB month arithmetic, including month-end clamping.
    month_index = end.year * 12 + end.month - 1 - months
    year, month = divmod(month_index, 12)
    month += 1
    start = date(year, month, min(end.day, calendar.monthrange(year, month)[1]))
    sql = """
        SELECT CAST(ListingKey AS CHAR) AS listingId,
          UnparsedAddress AS address, City AS city, CloseDate AS closeDate,
          ClosePrice AS price, BedroomsTotal AS beds,
          BathroomsTotalInteger AS baths, LivingArea AS sqft,
          PropertySubType AS type, DaysOnMarket AS daysOnMarket
        FROM california_sold
        WHERE City = %s AND PropertyType = %s
          AND CloseDate REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
          AND CloseDate >= %s AND CloseDate <= %s AND ClosePrice > 0
        ORDER BY CloseDate DESC, ListingKey DESC
        LIMIT %s OFFSET %s
    """
    params = [city.strip(), "Residential", start.isoformat(), as_of, limit + 1, offset]
    return sql, params, as_of


def get_sold_comps(city, months=12, page=1, limit=5, as_of=None):
    sql, params, as_of = build_sold_query(city, months, page, limit, as_of)
    rows = query(sql, params)
    return dict(city=city.strip(), months=months, asOf=as_of, page=page,
                limit=limit, hasMore=len(rows) > limit, properties=rows[:limit])
