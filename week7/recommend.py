"""Recommend active listings using structured scores and cached Gemini vectors."""
import argparse
import calendar
import math
import sqlite3
import sys
from datetime import date
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week3.db import query, json_text
from week6.semantic import CACHE, MODEL, DIMENSIONS, SELECT, listing_text, fingerprint, normalize


def number(value, allow_zero=False):
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) and (result >= 0 if allow_zero else result > 0) else None


def similarity_score(target, candidate, target_vector, candidate_vector):
    parts = {'price': 0, 'beds': 0, 'city': 0, 'sqft': 0}
    price_a, price_b = number(target.get('price')), number(candidate.get('price'))
    if price_a is not None and price_b is not None:
        difference = abs(price_a - price_b)
        parts['price'] = 20 if difference < 50000 else 12 if difference < 150000 else 5 if difference < 300000 else 0
    beds_a, beds_b = number(target.get('beds'), True), number(candidate.get('beds'), True)
    if beds_a is not None and beds_a == beds_b:
        parts['beds'] = 15
    city_a, city_b = target.get('city'), candidate.get('city')
    if isinstance(city_a, str) and isinstance(city_b, str) and city_a.strip() and city_a.strip().casefold() == city_b.strip().casefold():
        parts['city'] = 15
    area_a, area_b = number(target.get('sqft')), number(candidate.get('sqft'))
    if area_a is not None and area_b is not None:
        difference = abs(area_a - area_b)
        parts['sqft'] = 10 if difference < 300 else 5 if difference < 700 else 0
    cosine = float(np.clip(np.dot(normalize(target_vector), normalize(candidate_vector)), -1, 1))
    structured = sum(parts.values())
    semantic = cosine * 40
    return {'total': structured + semantic, 'structured_points': structured,
            'semantic_points': semantic, 'cosine_similarity': cosine,
            'structured_breakdown': parts}


def subtract_months(day, months):
    year, month_zero = divmod(day.year * 12 + day.month - 1 - months, 12)
    month = month_zero + 1
    return date(year, month, min(day.day, calendar.monthrange(year, month)[1]))


def assess_price(candidate, as_of):
    area, price = number(candidate.get('sqft')), number(candidate.get('price'))
    start = subtract_months(as_of, 6)
    criteria = {'city': candidate.get('city'), 'property_subtype': candidate.get('property_type'),
                'from': start.isoformat(), 'through': as_of.isoformat(),
                'sqft_min': area * 0.8 if area else None, 'sqft_max': area * 1.2 if area else None}
    result = {'criteria': criteria, 'comp_count': 0, 'average_sold_price_per_sqft': None,
              'comp_based_price': None, 'list_price': price, 'difference_pct': None,
              'assessment': 'unavailable', 'first_comp_date': None, 'last_comp_date': None}
    if area is None or price is None or not candidate.get('city'):
        result['reason'] = 'Missing valid city, asking price, or square footage.'
        return result
    sql = '''SELECT CloseDate AS close_date, ClosePrice AS price, LivingArea AS sqft
             FROM california_sold WHERE City = %s AND PropertyType = %s
             AND LivingArea BETWEEN %s AND %s AND ClosePrice > 0
             AND CloseDate >= %s AND CloseDate <= %s'''
    params = [candidate['city'], 'Residential', area * 0.8, area * 1.2,
              start.isoformat(), as_of.isoformat()]
    # Use the same subtype where known, avoiding a broad mix of condos and houses.
    if candidate.get('property_type'):
        sql += ' AND PropertySubType = %s'
        params.append(candidate['property_type'])
    ratios, dates = [], []
    for row in query(sql, params):
        try:
            closed = date.fromisoformat(row['close_date'])
            if row['close_date'] != closed.isoformat() or not start <= closed <= as_of:
                continue
        except (ValueError, TypeError):
            continue
        sold_price, sold_area = number(row['price']), number(row['sqft'])
        if sold_price is not None and sold_area is not None and area * 0.8 <= sold_area <= area * 1.2:
            ratios.append(sold_price / sold_area)
            dates.append(closed.isoformat())
    if not ratios:
        result['reason'] = 'No valid recent sold comparables matched these criteria in the snapshot.'
        return result
    average = sum(ratios) / len(ratios)
    baseline = average * area
    result.update(comp_count=len(ratios), average_sold_price_per_sqft=round(average, 2),
                  comp_based_price=round(baseline, 2), difference_pct=round((price / baseline - 1) * 100, 2),
                  assessment='limited_sample' if len(ratios) < 5 else 'comparison_available',
                  first_comp_date=min(dates), last_comp_date=max(dates))
    return result


def cached_listings():
    if not CACHE.is_file():
        raise ValueError('Week 6 index is missing. Build the index first.')
    connection = sqlite3.connect(CACHE.resolve().as_uri() + '?mode=ro', uri=True)
    try:
        cached = connection.execute('SELECT id, text_hash, vector FROM embeddings WHERE model = ? AND dimensions = ?',
                                    (MODEL, DIMENSIONS)).fetchall()
    finally:
        connection.close()
    fresh = {}
    for start in range(0, len(cached), 200):
        batch = cached[start:start + 200]
        placeholders = ','.join(['%s'] * len(batch))
        rows = query(SELECT + f' WHERE L_Status = %s AND id IN ({placeholders})',
                     ['Active'] + [item[0] for item in batch])
        current = {row['id']: row for row in rows}
        for listing_id, text_hash, blob in batch:
            row = current.get(listing_id)
            if row and fingerprint(listing_text(row)) == text_hash:
                fresh[listing_id] = (row, normalize(np.frombuffer(blob, dtype=np.float32)))
    return fresh


def recommend(listing_id, top=5, as_of=None):
    if type(top) is not int or not 1 <= top <= 20:
        raise ValueError('Top must be an integer from 1 to 20.')
    end = date.fromisoformat(as_of) if as_of else date.today()
    targets = query(SELECT + ' WHERE L_ListingID = %s AND L_Status = %s LIMIT 2', (listing_id, 'Active'))
    if len(targets) != 1:
        raise ValueError('The listing ID must identify exactly one active reference listing.')
    target = targets[0]
    fresh = cached_listings()
    if target['id'] not in fresh:
        raise ValueError('The reference listing has no fresh embedding. Refresh its city with the Week 6 build command.')
    target_vector = fresh[target['id']][1]
    ranked = []
    for internal_id, (candidate, vector) in fresh.items():
        if internal_id == target['id'] or str(candidate.get('listing_id')) == str(listing_id):
            continue
        score = similarity_score(target, candidate, target_vector, vector)
        ranked.append((candidate, score))
    ranked.sort(key=lambda item: (-item[1]['total'], item[0]['id']))
    recommendations = []
    for candidate, score in ranked[:top]:
        card = {key: value for key, value in candidate.items() if key != 'remarks'}
        card['score'] = {key: round(value, 4) if isinstance(value, float) else value for key, value in score.items()}
        card['price_comparison'] = assess_price(candidate, end)
        recommendations.append(card)
    return {'source': 'Imported MLS snapshot; not live availability', 'as_of': end.isoformat(),
            'target': {key: value for key, value in target.items() if key != 'remarks'},
            'indexed_candidates_scored': len(ranked), 'model': MODEL,
            'scoring': 'Up to 60 structured points plus 40 times embedding cosine similarity; not a probability.',
            'recommendations': recommendations,
            'notes': ['Only fresh, active indexed listings are considered; the initial index covers Irvine.',
                      'The reference listing is excluded. Scores rank similarity, not investment quality.',
                      'Sold comparisons use the same city and known subtype, +/-20% square footage, and the prior six months.',
                      'Positive difference_pct means the asking price is above the sold-comparable baseline; negative means below.',
                      'The baseline is average sold price per sqft times candidate sqft, not an appraisal or proof a price is fair.',
                      'Fewer than five comparables is flagged as limited_sample. Missing comparisons remain unavailable.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('listing_id')
    parser.add_argument('--top', type=int, default=5)
    parser.add_argument('--as-of')
    args = parser.parse_args()
    try:
        print(json_text(recommend(args.listing_id, args.top, args.as_of)))
    except Exception as error:
        message = str(error) if isinstance(error, ValueError) else type(error).__name__ + ': check MySQL and the Week 6 index.'
        print('Recommendation failed: ' + message, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
