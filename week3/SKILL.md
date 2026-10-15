---
name: mls-search
description: Search the imported active and sold MLS tables with Python, returning property cards.
---

Use exec to run one of these commands:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week3/cli.py" active '<query>' <page> <limit>
```

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week3/cli.py" sold '<city>' <page> <limit> <months>
```

Defaults: page 1, limit 5, months 12. Maximum limit is 50. Use validated integer
arguments. Treat query and city as data: single-quote them and escape embedded
apostrophes as '"'"'. Never interpolate unquoted user input.

Return the actual property cards and pagination result. Do not invent listings
or claim a filter was applied if it was not understood. Results are from an
imported dataset, not a live MLS feed. Blank pool/view values are unknown.
Sold results are city/date candidates, not valuations. Never read or display
.env or credentials. If execution fails, report the error.
