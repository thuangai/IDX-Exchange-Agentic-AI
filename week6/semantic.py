"""Build a cached Gemini property index, then search it by meaning."""
import argparse
import hashlib
import os
import sqlite3
import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from week3.db import query, json_text

MODEL = 'gemini-embedding-001'
DIMENSIONS = 3072
CACHE = ROOT / 'data' / 'week6-semantic.sqlite'
SELECT = '''SELECT id, L_ListingID AS listing_id, L_Address AS address,
    L_City AS city, L_SystemPrice AS price, L_Type_ AS property_type,
    L_Keyword2 AS beds, LM_Dec_3 AS baths, LM_Int2_3 AS sqft,
    L_Remarks AS remarks FROM rets_property'''


def listing_text(row):
    def value(key):
        return row.get(key) if row.get(key) is not None else 'unknown'
    # Bound input size conservatively; this is a character cap, not a token count.
    return (f"{value('property_type')} in {value('city')}, California. "
            f"{value('beds')} beds; {value('baths')} baths; {value('sqft')} sqft. "
            f"List price: {value('price')}. Description: {value('remarks')}")[:6000]


def fingerprint(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def normalize(values):
    vector = np.asarray(values, dtype=np.float32)
    if vector.shape != (DIMENSIONS,) or not np.all(np.isfinite(vector)):
        raise ValueError('Invalid embedding dimensions or values.')
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError('Embedding has zero length.')
    return vector / norm


def embed(texts, task):
    from google import genai
    from google.genai import types
    for path in (ROOT / 'week3' / '.env', ROOT / '.env'):
        if path.is_file():
            load_dotenv(path)
            break
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        raise ValueError('Add GEMINI_API_KEY to week3/.env first.')
    with genai.Client(api_key=key) as client:
        response = client.models.embed_content(
            model=MODEL, contents=texts,
            config=types.EmbedContentConfig(task_type=task))
    embeddings = response.embeddings or []
    if len(embeddings) != len(texts):
        raise ValueError('The API returned an unexpected number of embeddings.')
    return [normalize(item.values) for item in embeddings]


def open_cache():
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(CACHE)
    connection.execute('''CREATE TABLE IF NOT EXISTS embeddings (
        id INTEGER PRIMARY KEY, model TEXT NOT NULL, dimensions INTEGER NOT NULL,
        text_hash TEXT NOT NULL, vector BLOB NOT NULL)''')
    return connection


def build(city=None, limit=100):
    conditions = ['L_Status = %s', 'NULLIF(TRIM(L_Remarks), %s) IS NOT NULL']
    params = ['Active', '']
    if city:
        conditions.append('L_City = %s')
        params.append(city)
    sql = SELECT + ' WHERE ' + ' AND '.join(conditions) + ' ORDER BY id'
    if limit:
        sql += ' LIMIT %s'
        params.append(limit)
    rows = query(sql, params)
    if not rows:
        raise ValueError('No active listings with descriptions matched.')
    connection = open_cache()
    updated = 0
    try:
        pending = []
        for row in rows:
            text = listing_text(row)
            old = connection.execute('SELECT model, dimensions, text_hash FROM embeddings WHERE id = ?',
                                     (row['id'],)).fetchone()
            if old != (MODEL, DIMENSIONS, fingerprint(text)):
                pending.append((row, text))
        print(f'Selected {len(rows)} listings; {len(pending)} need embeddings.', flush=True)
        # Save each batch so an interrupted build can resume without redoing saved calls.
        for start in range(0, len(pending), 10):
            batch = pending[start:start + 10]
            vectors = embed([text for _, text in batch], 'RETRIEVAL_DOCUMENT')
            for (row, text), vector in zip(batch, vectors):
                connection.execute('INSERT OR REPLACE INTO embeddings VALUES (?, ?, ?, ?, ?)',
                                   (row['id'], MODEL, DIMENSIONS, fingerprint(text), vector.tobytes()))
            connection.commit()
            updated += len(batch)
            print(f'Saved {updated}/{len(pending)} new embeddings.', flush=True)
        print(f'Index ready. Cache: {CACHE}')
        print('Search covers indexed listings only, not necessarily the full dataset.')
    finally:
        connection.close()


def search(text, city=None, top=5):
    if not text.strip():
        raise ValueError('Enter a search description.')
    if not CACHE.is_file():
        raise ValueError('Build an index first.')
    connection = open_cache()
    try:
        cached = connection.execute('SELECT id, text_hash, vector FROM embeddings '
                                    'WHERE model = ? AND dimensions = ?', (MODEL, DIMENSIONS)).fetchall()
    finally:
        connection.close()
    # Recheck active status and text against MySQL rather than serving stale cached listings.
    candidates = []
    for start in range(0, len(cached), 200):
        batch = cached[start:start + 200]
        placeholders = ','.join(['%s'] * len(batch))
        sql = SELECT + f' WHERE L_Status = %s AND id IN ({placeholders})'
        params = ['Active'] + [item[0] for item in batch]
        if city:
            sql += ' AND L_City = %s'
            params.append(city)
        current = {row['id']: row for row in query(sql, params)}
        for listing_id, text_hash, blob in batch:
            row = current.get(listing_id)
            if row and fingerprint(listing_text(row)) == text_hash:
                candidates.append((row, normalize(np.frombuffer(blob, dtype=np.float32))))
    if not candidates:
        raise ValueError('No fresh indexed listings match. Build or refresh the index for this city.')
    vector = embed([text[:6000]], 'RETRIEVAL_QUERY')[0]
    scores = np.stack([item[1] for item in candidates]) @ vector
    order = np.argsort(-scores, kind='stable')[:top]
    results = []
    for index in order:
        row = dict(candidates[int(index)][0])
        row['similarity'] = round(float(scores[index]), 4)
        results.append(row)
    return {'query': text, 'city': city, 'model': MODEL,
            'indexed_candidates_searched': len(candidates),
            'note': 'Cosine similarity ranks meaning; it is not a probability or a guarantee of features. '
                    'Results cover only fresh, active listings in the local index.',
            'properties': results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    builder = commands.add_parser('build')
    builder.add_argument('--city')
    builder.add_argument('--limit', type=int, default=100, help='Default 100; 0 selects all matching listings.')
    finder = commands.add_parser('search')
    finder.add_argument('text')
    finder.add_argument('--city')
    finder.add_argument('--top', type=int, default=5)
    args = parser.parse_args()
    if args.command == 'build' and args.limit < 0:
        parser.error('--limit cannot be negative.')
    if args.command == 'search' and not 1 <= args.top <= 50:
        parser.error('--top must be from 1 to 50.')
    try:
        if args.command == 'build':
            build(args.city, args.limit)
        else:
            print(json_text(search(args.text, args.city, args.top)))
    except Exception as error:
        # Provider errors may contain request details. Report only their type, never credentials.
        if isinstance(error, ValueError):
            print(f'Semantic search failed: {error}', file=sys.stderr)
        else:
            code = getattr(error, 'code', None)
            print(f'Semantic search failed: {type(error).__name__}'
                  + (f' (code {code})' if isinstance(code, int) else '')
                  + '. Check MySQL, API quota, and your local settings.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
