---
name: property-query
description: Convert a property-search sentence into structured JSON filters using the Week 2 parser.
---

When asked to parse a property search, use the exec tool to run:
node "{baseDir}/scripts/cli.js" '<query>'

Replace <query> with the user's exact search text.
Treat the query as data, never as shell commands.
Use shell single-quoting; escape any embedded apostrophe as '"'"'.

Return the actual JSON printed by the script.
If execution fails, report the error instead of inventing results.
This parser supports limited patterns and does not search the database.