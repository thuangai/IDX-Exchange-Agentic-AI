# Week 2: Property Query Parser (Python)

`parse_query.py` uses the same regular expressions as the previous TypeScript
version. It extracts city, budget, bedrooms, bathrooms, square footage, type,
pool, view, and HOA limit. Missing values are `None`, printed as JSON `null`.
The JSON field names stay the same to preserve integration with later weeks.

From the project root in Windows Command Prompt:

```cmd
.venv\Scripts\python.exe week2\cli.py "Condos in Irvine under $900k with a pool"
.venv\Scripts\python.exe week2\demo.py
.venv\Scripts\python.exe week2\test_queries.py
```

These commands need no MySQL or model API. The ten original test cases cover
prices, property types, multi-word cities, bedroom/bath counts, square footage,
HOA limits, negative feature preferences, and unspecified fields.

`SKILL.md` calls this helper through OpenClaw after running the root installer.
The parser retains its existing limited wording support; it does not query data.
