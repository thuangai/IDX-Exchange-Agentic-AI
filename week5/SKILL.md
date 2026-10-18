---
name: market-statistics
description: Answer California real estate market questions using the imported MLS snapshot. Use for median or average sold prices, price per square foot, days on market, list-to-close ratios, active inventory, monthly trends, and questions about whether market conditions favor buyers.
---

Ask for a city if none is supplied. Extract ZIP and property subtype only when requested.
Run the statistics helper and the trends helper to answer a general market question:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week5/stats.py" 'Irvine'
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week5/trends.py" 'Irvine' --json
```

Replace Irvine with the requested city. Shell-quote all arguments safely. Both helpers accept
--zip '92618', --type 'Condominium', --months 12, and --as-of '2026-10-18'.
Use canonical subtype names such as Condominium, Townhouse, or SingleFamilyResidence.
Keep the same filters and as-of date across both calls. Use the default date unless the user requests another.
For a narrow question, run only the helper needed. Never retry successful calls in a loop.

Summarize actual returned values in plain language. For a general overview include median price,
average days on market, average list-to-close percentage, sold count, active snapshot count,
and the available monthly trend. Explain that a ratio of 98% means sales averaged 2% below
their list prices. The ratio uses ListPrice, not OriginalListPrice.

State that the source is an imported snapshot and give the observed sale-date range.
Do not describe the active count as live inventory or treat absent records as proof of zero market sales.
Keep missing values unavailable; never invent year-over-year figures, missing months, or coverage.
Mention that boundary months can be incomplete, especially the first and last observed months.
Describe monthly price changes as changes in the mix of homes sold, not appreciation of the same homes.
For a buyer-timing question, explain the measured indicators and data limits without declaring a
definitive current buy/sell recommendation from this snapshot.
If no sales match, report that and ask whether to broaden the filters.
If execution fails, report the actual error briefly; do not substitute invented results.
Never read or print .env, database passwords, or API keys in a reply.
