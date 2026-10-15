"""Active searches: fixed column names, bound filter and pagination values."""
import math
from week3.db import query


def pagination(page, limit):
    if type(page) is not int or page < 1:
        raise ValueError("Page must be a positive integer.")
    if type(limit) is not int or not 1 <= limit <= 50:
        raise ValueError("Limit must be between 1 and 50.")
    offset = (page - 1) * limit
    if offset > 9_007_199_254_740_991:
        raise ValueError("Page is too large.")
    return offset


def build_active_query(filters, page=1, limit=5):
    offset = pagination(page, limit)
    conditions = ["L_Status = %s"]
    params = ["Active"]

    for key, column in (("city", "L_City"), ("type", "L_Type_")):
        value = filters.get(key)
        if value is not None:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"Invalid value for {key}.")
            conditions.append(f"{column} = %s")
            params.append(value)

    for key, condition in (
        ("maxPrice", "L_SystemPrice <= %s"),
        ("beds", "L_Keyword2 >= %s"),
        ("baths", "LM_Dec_3 >= %s"),
        ("sqft", "LM_Int2_3 >= %s"),
        ("maxHOA", "AssociationFee <= %s"),
    ):
        value = filters.get(key)
        if value is not None:
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid value for {key}.")
            conditions.append(condition)
            params.append(value)

    for key, column in (("pool", "PoolPrivateYN"), ("hasView", "ViewYN")):
        value = filters.get(key)
        if value is not None:
            if value not in ("True", "False"):
                raise ValueError(f"Invalid value for {key}.")
            conditions.append(f"LOWER(TRIM({column})) IN (%s, %s)")
            params.extend(("1" if value == "True" else "0", value.lower()))

    sql = """
        SELECT id, L_ListingID AS listingId,
          L_Address AS address, L_City AS city, L_Zip AS zip,
          L_SystemPrice AS price, L_Keyword2 AS beds,
          LM_Dec_3 AS baths, LM_Int2_3 AS sqft,
          L_Type_ AS type, L_Status AS status, PhotoCount AS photoCount,
          AssociationFee AS hoa, PoolPrivateYN AS pool, ViewYN AS hasView
        FROM rets_property
        WHERE """ + " AND ".join(conditions) + """
        ORDER BY L_SystemPrice ASC, id ASC
        LIMIT %s OFFSET %s
    """
    params.extend((limit + 1, offset))
    return sql, params


def search_active_listings(filters, page=1, limit=5):
    sql, params = build_active_query(filters, page, limit)
    rows = query(sql, params)
    return dict(page=page, limit=limit, hasMore=len(rows) > limit, properties=rows[:limit])
