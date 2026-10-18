"""Week 5: calculate market statistics from the imported MLS snapshot.

Run from the project root: python week5/stats.py Irvine
Uses week3/db.py and the existing private .env settings.
"""
import argparse
import calendar
import math
import sys
from datetime import date
from pathlib import Path
from statistics import mean, median

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week3.db import query, json_text


def positive_number(value):
    """Return a usable positive number; missing and zero are not measurements."""
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def summarize(rows):
    prices, per_sqft, ratios, days, dates = [], [], [], [], []
    for row in rows:
        price = positive_number(row['price'])
        if price is None:
            continue
        prices.append(price)
        dates.append(row['close_date'])
        area = positive_number(row['sqft'])
        listing_price = positive_number(row['list_price'])
        if area is not None:
            per_sqft.append(price / area)
        if listing_price is not None:
            ratios.append(price / listing_price * 100)
        try:
            dom = float(row['days_on_market'])
            if math.isfinite(dom) and dom >= 0:
                days.append(dom)
        except (ValueError, TypeError):
            pass

    def average(values):
        return round(mean(values), 2) if values else None

    return {
        'sold_count': len(prices),
        'average_close_price': average(prices),
        'median_close_price': round(median(prices), 2) if prices else None,
        'average_price_per_sqft': average(per_sqft),
        'average_days_on_market': average(days),
        'average_list_to_close_pct': average(ratios),
        'metric_sample_counts': {
            'price_per_sqft': len(per_sqft),
            'days_on_market': len(days),
            'list_to_close': len(ratios),
        },
        'first_sale_date': min(dates) if dates else None,
        'last_sale_date': max(dates) if dates else None,
    }


def market_summary(city, months=12, as_of=None, zip_code=None, property_type=None):
    if not isinstance(city, str) or not city.strip():
        raise ValueError('Enter a city.')
    if type(months) is not int or not 1 <= months <= 120:
        raise ValueError('Months must be an integer from 1 to 120.')
    end = date.fromisoformat(as_of) if as_of else date.today()
    month_index = end.year * 12 + end.month - 1 - months
    year, month_zero = divmod(month_index, 12)
    start = date(year, month_zero + 1,
                 min(end.day, calendar.monthrange(year, month_zero + 1)[1]))

    sold_where = ['City = %s', 'PropertyType = %s',
                  'CloseDate >= %s', 'CloseDate <= %s', 'ClosePrice > 0']
    sold_params = [city.strip(), 'Residential', start.isoformat(), end.isoformat()]
    active_where = ['L_City = %s', 'L_Status = %s']
    active_params = [city.strip(), 'Active']
    if zip_code:
        sold_where.append('PostalCode = %s')
        sold_params.append(zip_code)
        active_where.append('L_Zip = %s')
        active_params.append(zip_code)
    if property_type:
        sold_where.append('PropertySubType = %s')
        sold_params.append(property_type)
        active_where.append('L_Type_ = %s')
        active_params.append(property_type)

    # Only fixed SQL fragments are combined. All user values remain bound parameters.
    rows = query('''SELECT CloseDate AS close_date, ClosePrice AS price,
                    ListPrice AS list_price, LivingArea AS sqft,
                    DaysOnMarket AS days_on_market
                    FROM california_sold WHERE ''' + ' AND '.join(sold_where), sold_params)
    valid_rows = []
    for row in rows:
        try:
            raw_date = row['close_date']
            parsed_date = date.fromisoformat(raw_date)
            if raw_date == parsed_date.isoformat() and start <= parsed_date <= end:
                valid_rows.append(row)
        except (ValueError, TypeError):
            continue

    active = query('SELECT COUNT(*) AS total FROM rets_property WHERE '
                   + ' AND '.join(active_where), active_params)[0]['total']
    return {
        'source': 'Imported MLS snapshot (not live inventory)',
        'city': city.strip(),
        'zip': zip_code,
        'property_type': property_type,
        'requested_window': {'from': start.isoformat(), 'through': end.isoformat()},
        **summarize(valid_rows),
        'active_listings_in_snapshot': int(active),
        'notes': [
            'Sale dates show observed records, not proof of complete monthly coverage.',
            'Metrics omit missing or invalid values; sample counts may differ.',
            'List-to-close uses ClosePrice / ListPrice, not OriginalListPrice.',
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('city')
    parser.add_argument('--months', type=int, default=12)
    parser.add_argument('--as-of', help='YYYY-MM-DD; defaults to today')
    parser.add_argument('--zip', dest='zip_code')
    parser.add_argument('--type', dest='property_type', help='E.g. Condominium')
    args = parser.parse_args()
    try:
        print(json_text(market_summary(**vars(args))))
    except Exception as error:
        print(f'Market statistics failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
