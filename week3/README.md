# Week 3: MLS Database Integration (Python)

Uses `mysql-connector-python` and `python-dotenv` with the existing MySQL schema.
Database code lives in `db.py`; active searches in `search.py`; recent sales in
`sold.py`; property cards in `format.py`. CLI arguments remain the same.

Keep your existing `week3/.env` and use a MySQL account with SELECT access.
Start MySQL inside Ubuntu and keep that terminal open. See the root README.

From the project root in Windows Command Prompt:

```cmd
.venv\Scripts\python.exe week3\test_db.py
.venv\Scripts\python.exe week3\cli.py active "Condos in Irvine under $900k" 1 5
.venv\Scripts\python.exe week3\cli.py active "Condos in Irvine under $900k" 2 5
.venv\Scripts\python.exe week3\cli.py sold Irvine 1 5 12
.venv\Scripts\python.exe week3\test_search.py "Condos in Irvine under $900k"
.venv\Scripts\python.exe week3\test_sold.py Irvine 12
```

`test_db.py`, `test_search.py`, and `test_sold.py` are manual live checks.
The root `tests` folder provides offline automated regression tests.

Filter values, LIMIT, and OFFSET use connector placeholders. Sort columns and
filter columns are fixed in code. Active results include photo counts; unknown
pool/view values do not match an explicit false request. Pages are sorted with
a stable ID tiebreaker and fetch one extra result to determine `hasMore`.

Sold date bounds are calculated in Python with month-end clamping, then bound
to the SQL query. This preserves the prior date window without MySQL-specific
date arithmetic in the query. Future sales and nonpositive prices are excluded.
The existing CloseDate YYYY-MM-DD format check is retained.

Results are from an imported snapshot. Sold candidates are not valuations.
Decimal database values are supported by the JSON and card formatters.
