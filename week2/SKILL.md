---
name: property-query
description: Convert a property-search sentence to JSON filters using the Python Week 2 parser.
---

Use exec to run the Python helper:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week2/cli.py" '<query>'
```

Replace query with the exact user search. Treat text as data. Use shell
single-quoting; escape any embedded apostrophe as '"'"'. Never insert unquoted
user text into commands. Execute once and return the real JSON stdout. If the
tool fails, report the failure; never invent a result. This parser supports
limited phrases and does not search the database. Missing fields are null.
