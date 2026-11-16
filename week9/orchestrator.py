"""Coordinate existing helpers without building indexes or sending emails."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week2.parse_query import parse_property_query
from week3.db import json_text

ORDER = ('propertySearchAgent', 'marketStatsAgent', 'recommendationAgent', 'ragAgent')


def plan(query):
    """Transparent rules; explicit CLI hints resolve unsupported natural language."""
    text = query.lower()
    email = bool(re.search(r'\b(email|draft|compose)\b', text))
    knowledge = bool(re.search(r'\b(what (?:is|are|does)|define|definition|explain|meaning|schema|columns?|fields?)\b', text))
    market = bool(re.search(r'\b(market|trends?|rising|falling|statistics|median|average|comps|prices? (?:are|going|rising|falling))\b', text))
    search = bool(re.search(r'\b(find|search|show|list)\b.{0,50}\b(homes?|houses?|properties|listings?|condos?|townhomes?)\b', text))
    recommend = bool(re.search(r'\b(recommend\w*|similar|alternatives?)\b', text))
    # A question about a definition must not become a market-data request solely
    # because the defined phrase includes "market" or "average".
    if knowledge and not re.search(r'\b(and|also|then)\b', text) and not search and not recommend:
        market = False
    selected = {name for flag, name in [(search, ORDER[0]), (market, ORDER[1]),
                (recommend, ORDER[2]), (knowledge, ORDER[3])] if flag}
    return [name for name in ORDER if name in selected] + (['emailDraftAgent'] if email else [])


def state_path(session_id):
    if not session_id or not session_id.strip():
        raise ValueError('A trusted session ID is required.')
    folder = Path(os.environ.get('IDX_WEEK9_SESSION_DIR', str(Path.home() / '.idx-exchange/week9-sessions')))
    return folder / (hashlib.sha256(session_id.encode()).hexdigest() + '.json')


def save_state(path, value):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(json_text(value))
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def run_agent(name, request):
    # Lazy imports keep routing/tests offline and reuse each original helper.
    if name == ORDER[0]:
        from week3.search import search_active_listings
        return search_active_listings(request['filters'], 1, 5)
    if name == ORDER[1]:
        from week5.stats import market_summary
        from week5.trends import market_trends
        options = dict(city=request['filters']['city'], months=request['months'], as_of=request['as_of'])
        return dict(summary=market_summary(**options), trends=market_trends(**options))
    if name == ORDER[2]:
        from week7.recommend import recommend
        return recommend(request['listing_id'], as_of=request['as_of'])
    if name == ORDER[3]:
        from week8.rag import answer
        return answer(request['query'])
    raise ValueError('Unknown agent.')


def compose(results):
    """Keep citations and numeric evidence intact rather than regenerate claims."""
    sections = []
    for name in ORDER:
        if name in results:
            item = results[name]
            content = item['data'] if item['status'] == 'ok' else item['message']
            sections.append(name + '\n' + (content if isinstance(content, str) else json_text(content)))
    return '\n\n'.join(sections)


def orchestrate(query, session_id, city=None, listing_id=None, months=12, as_of=None,
                runner=None, agents=None):
    if not query.strip() or len(query) > 6000:
        raise ValueError('Enter a query between 1 and 6,000 characters.')
    if type(months) is not int or not 1 <= months <= 120:
        raise ValueError('Months must be between 1 and 120.')
    if as_of:
        from datetime import date
        date.fromisoformat(as_of)
    path = state_path(session_id)
    if re.fullmatch(r'(start over|reset|new search)[.!]?', query.strip(), re.I):
        path.unlink(missing_ok=True)
        return dict(status='ok', agents=[], response='Session cleared. What would you like to search?')
    saved = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    selected = agents or plan(query)
    if any(name not in (*ORDER, 'emailDraftAgent') for name in selected):
        raise ValueError('Unknown agent selection.')
    filters = {**saved.get('filters', {}), **{k: v for k, v in parse_property_query(query).items() if v is not None}}
    if city:
        filters['city'] = city.strip()
    explicit_id = re.search(r'\blisting\s*(?:id\s*)?[:#]?\s*(\d+)\b', query, re.I)
    reference = listing_id or (explicit_id[1] if explicit_id else None) or saved.get('last_listing_id')
    # A saved search can be refined using the original Week 2 supported filters.
    if not selected and saved.get('filters') and any(v is not None for v in parse_property_query(query).values()):
        selected = [ORDER[0]]
    if not selected:
        return dict(status='clarification', agents=[], response='Ask for property search, market statistics, similar listings, document knowledge, or an email draft.')
    request = dict(query=query, filters=filters, listing_id=reference, months=months, as_of=as_of)
    results, jobs = {}, []
    for name in selected:
        if name == 'emailDraftAgent':
            continue
        if name in ORDER[:2] and not filters.get('city'):
            results[name] = dict(status='clarification', message='Which city? Supply --city or include "in CITY" in your question.')
        elif name == ORDER[2] and not reference:
            results[name] = dict(status='clarification', message='Which listing ID should I use as the reference?')
        else:
            jobs.append(name)
    def invoke(name):
        try:
            return dict(status='ok', data=(runner or run_agent)(name, request))
        except Exception as error:
            # Raw connector errors can include credentials or connection details.
            return dict(status='error', message=f'{name} failed ({type(error).__name__}). Check the installed helper, database, index, or API quota.')
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {name: pool.submit(invoke, name) for name in jobs}
        for name, future in futures.items():
            results[name] = future.result()
    evidence = compose(results)
    successful = {name: item for name, item in results.items() if item['status'] == 'ok'}
    if successful:
        saved['filters'] = filters
        found = successful.get(ORDER[0], {}).get('data', {}).get('properties', [])
        saved['last_listing_id'] = (found[0].get('listingId') if found else saved.get('last_listing_id'))
        if ORDER[2] in successful:
            saved['last_listing_id'] = reference
        saved['last_evidence'] = evidence
        save_state(path, saved)
    if 'emailDraftAgent' in selected:
        # Failed fresh retrieval never falls back silently to old facts.
        body = compose(successful) if results else saved.get('last_evidence', '')
        if body:
            draft = 'Subject: Property and market summary\n\nHello,\n\nHere is the requested summary:\n\n' + body + '\n\nSource: imported MLS snapshot and/or cited indexed documents; not live availability.\n\nBest regards'
            results['emailDraftAgent'] = dict(status='ok', data=draft)
        else:
            results['emailDraftAgent'] = dict(status='clarification', message='Ask for a property search or market summary first, or include it in the draft request.')
    statuses = [item['status'] for item in results.values()]
    status = 'ok' if all(s == 'ok' for s in statuses) else ('partial' if 'ok' in statuses else ('clarification' if 'clarification' in statuses else 'error'))
    response = results.get('emailDraftAgent', {}).get('data', evidence)
    if 'emailDraftAgent' in results and results['emailDraftAgent']['status'] != 'ok':
        response += '\n\n' + results['emailDraftAgent']['message']
    if status == 'partial' and results.get('emailDraftAgent', {}).get('status') == 'ok':
        response += '\n\nIncomplete request: some agents failed or need clarification. See agent results.'
    return dict(status=status, agents=selected, results=results, response=response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('session_id')
    parser.add_argument('query')
    parser.add_argument('--city')
    parser.add_argument('--listing-id')
    parser.add_argument('--months', type=int, default=12)
    parser.add_argument('--as-of')
    parser.add_argument('--agents', nargs='+', choices=(*ORDER, 'emailDraftAgent'))
    parser.add_argument('--plan', action='store_true', help='Inspect routing offline; no database or API calls')
    args = vars(parser.parse_args())
    inspect = args.pop('plan')
    try:
        if inspect:
            print(json_text({'agents': args['agents'] or plan(args['query'])}))
            return 0
        result = orchestrate(**args)
        print(json_text(result))
        return 1 if result['status'] == 'error' else 0
    except Exception as error:
        print(f'Coordinator failed ({type(error).__name__}). Check the arguments or session file.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
