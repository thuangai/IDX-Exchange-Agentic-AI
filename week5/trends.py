"""Monthly sold-market trends. Run: python week5/trends.py Irvine"""
import argparse
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week3.db import query, json_text
from week5.stats import summarize


def month_start(reference, offset):
    index = reference.year * 12 + reference.month - 1 + offset
    year, month = divmod(index, 12)
    return date(year, month + 1, 1)


def percent_change(current, previous):
    if current is None or previous is None or previous <= 0:
        return None
    return round((current / previous - 1) * 100, 2)


def build_months(rows, end, months):
    first = month_start(end, 1 - months)
    buckets = {}
    for row in rows:
        try:
            sale_date = date.fromisoformat(row['close_date'])
            if row['close_date'] != sale_date.isoformat() or sale_date > end:
                continue
        except (ValueError, TypeError):
            continue
        key = sale_date.strftime('%Y-%m')
        buckets.setdefault(key, []).append(row)

    summaries = {key: summarize(items) for key, items in buckets.items()}
    output = []
    for offset in range(months):
        current_date = month_start(first, offset)
        key = current_date.strftime('%Y-%m')
        summary = summaries.get(key, summarize([]))
        previous = summaries.get(month_start(current_date, -1).strftime('%Y-%m'), {})
        last_year = summaries.get(month_start(current_date, -12).strftime('%Y-%m'), {})
        price = summary['median_close_price']
        output.append({
            'month': key,
            'sold_count': summary['sold_count'],
            'median_close_price': price,
            'average_close_price': summary['average_close_price'],
            'average_price_per_sqft': summary['average_price_per_sqft'],
            'average_days_on_market': summary['average_days_on_market'],
            'average_list_to_close_pct': summary['average_list_to_close_pct'],
            'median_price_mom_pct': percent_change(price, previous.get('median_close_price')),
            'median_price_yoy_pct': percent_change(price, last_year.get('median_close_price')),
            'price_per_sqft_mom_pct': percent_change(
                summary['average_price_per_sqft'], previous.get('average_price_per_sqft')),
            'first_observed_sale': summary['first_sale_date'],
            'last_observed_sale': summary['last_sale_date'],
            'is_current_partial_month': key == end.strftime('%Y-%m'),
        })
    return output


def market_trends(city, months=12, as_of=None, zip_code=None, property_type=None):
    if not isinstance(city, str) or not city.strip():
        raise ValueError('Enter a city.')
    if type(months) is not int or not 1 <= months <= 120:
        raise ValueError('Months must be an integer from 1 to 120.')
    end = date.fromisoformat(as_of) if as_of else date.today()
    # Fetch an additional year for comparisons, even when it is not displayed.
    start = month_start(end, 1 - months - 12)
    conditions = ['City = %s', 'PropertyType = %s', 'ClosePrice > 0',
                  'CloseDate >= %s', 'CloseDate <= %s']
    params = [city.strip(), 'Residential', start.isoformat(), end.isoformat()]
    if zip_code:
        conditions.append('PostalCode = %s')
        params.append(zip_code)
    if property_type:
        conditions.append('PropertySubType = %s')
        params.append(property_type)
    rows = query('''SELECT CloseDate AS close_date, ClosePrice AS price,
                    ListPrice AS list_price, LivingArea AS sqft,
                    DaysOnMarket AS days_on_market
                    FROM california_sold WHERE ''' + ' AND '.join(conditions), params)
    return {
        'source': 'Imported MLS snapshot (not live market data)',
        'city': city.strip(), 'zip': zip_code, 'property_type': property_type,
        'as_of': end.isoformat(),
        'months': build_months(rows, end, months),
        'notes': [
            'A zero count means no matching records in this snapshot; it does not prove zero market sales.',
            'Missing comparison data produces null, never a fabricated percentage.',
            'Monthly coverage is not guaranteed. First and last observed dates help spot partial months.',
            'Price changes describe the homes sold each month, not repeat sales of the same homes.',
        ],
    }


def display(result):
    print(f"Source: imported MLS snapshot | City: {result['city']} | Through: {result['as_of']}")
    print('Month     Sales     Median price    Avg $/sqft   Avg DOM    MoM %    YoY %')
    for item in result['months']:
        def value(key, digits=2):
            number = item[key]
            return f'{number:,.{digits}f}' if number is not None else 'N/A'
        print(f"{item['month']}  {item['sold_count']:>6}  {value('median_close_price', 0):>15}"
              f"  {value('average_price_per_sqft'):>12}  {value('average_days_on_market'):>8}"
              f"  {value('median_price_mom_pct'):>7}  {value('median_price_yoy_pct'):>7}")
    print('\nMoM and YoY compare median sold prices with the previous calendar month/year.')
    for note in result['notes']:
        print('- ' + note)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('city')
    parser.add_argument('--months', type=int, default=12)
    parser.add_argument('--as-of')
    parser.add_argument('--zip', dest='zip_code')
    parser.add_argument('--type', dest='property_type')
    parser.add_argument('--json', action='store_true', dest='as_json')
    args = vars(parser.parse_args())
    as_json = args.pop('as_json')
    try:
        result = market_trends(**args)
        print(json_text(result)) if as_json else display(result)
    except Exception as error:
        print(f'Market trends failed: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
