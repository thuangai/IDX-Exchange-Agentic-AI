"""Export schema references for Week 8 without exporting listing records or credentials."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from week3.db import query


def main():
    destination = ROOT / 'week8' / 'sources'
    destination.mkdir(parents=True, exist_ok=True)
    schemas = {}
    # These are fixed identifiers, never supplied by the user.
    for table in ('california_sold', 'rets_property', 'rets_openhouse'):
        rows = query('SHOW COLUMNS FROM `' + table + '`')
        schemas[table] = [{'name': row['Field'], 'type': row['Type'],
                           'nullable': row['Null'] == 'YES'} for row in rows]
    exported = datetime.now(timezone.utc).isoformat()
    payload = {'title': 'Actual imported IDX MySQL schema', 'exported_at': exported,
               'source': 'SHOW COLUMNS on the local idx_exchange database', 'tables': schemas}
    (destination / 'database_schema.json').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    for table, columns in schemas.items():
        lines = [f'# Actual database columns: {table}', '',
                 f'Source: SHOW COLUMNS on local idx_exchange; exported {exported}.',
                 'This is an observed schema, not the full Trestle API metadata.', '',
                 f'Table {table} has {len(columns)} columns:', '']
        lines += [f"- {item['name']}: {item['type']}; nullable={item['nullable']}" for item in columns]
        (destination / f'schema_{table}.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    mappings = {
        'L_ListingID': 'Listing identifier used by the project helpers.',
        'L_Address': 'Property address used by the project helpers.',
        'L_City': 'City used by the project helpers.',
        'L_Zip': 'ZIP/postal code used by the project helpers.',
        'L_Status': 'Listing status used for the Active filter.',
        'L_SystemPrice': 'Active asking/list price used by the project helpers.',
        'L_Keyword2': 'Bedroom count used by the project helpers.',
        'LM_Dec_3': 'Bathroom count used by the project helpers.',
        'LM_Int2_3': 'Living area/square footage used by the project helpers.',
        'L_Type_': 'Property subtype used by the project helpers, e.g. Condominium.',
        'L_Remarks': 'Listing description used by the Week 6 embedding helper.',
    }
    existing = {item['name'] for item in schemas['rets_property']}
    lines = ['# IDX legacy column reference', '',
             'Source: mappings implemented in this internship project (Weeks 2-7),',
             'checked against the exported rets_property column names.',
             'These are project interpretations, not official Trestle field definitions.', '',
             'Trestle metadata describes standard fields. Do not assume those standard names',
             'exist in rets_property; consult the actual schema and this legacy mapping.', '']
    lines += [f'- rets_property.{name}: {meaning}' for name, meaning in mappings.items() if name in existing]
    (destination / 'idx_legacy_mapping.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    for table, columns in schemas.items():
        print(f'{table}: exported {len(columns)} column definitions.')
    market_path = destination / 'irvine_market_summary.json'
    if market_path.is_file():
        try:
            json.loads(market_path.read_text(encoding='utf-8-sig'))
            print('Week 5 market summary: valid JSON.')
        except (ValueError, UnicodeError):
            print('Week 5 market summary is not valid UTF-8 JSON; regenerate it before indexing.')
    else:
        print('Week 5 market summary is missing; generate it before indexing.')
    print('Source preparation complete. No property records or credentials were exported.')


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(f'Source preparation failed: {type(error).__name__}. Check MySQL and your local settings.', file=sys.stderr)
        raise SystemExit(1)
