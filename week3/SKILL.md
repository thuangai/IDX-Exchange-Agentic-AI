---
name: mls-search
description: Search imported MLS active listings and recent residential sales, returning property cards.
---

Use this skill for property searches and sold-property comparisons.

Run the helper with the exec tool from the skill directory:
cd "{baseDir}" && /home/openclaw/.openclaw/tools/node-v24.19.0/bin/node dist/week3/cli.js active '<query>' <page> <limit>

For sold properties:
cd "{baseDir}" && /home/openclaw/.openclaw/tools/node-v24.19.0/bin/node dist/week3/cli.js sold '<city>' <page> <limit> <months>

Defaults: page 1, limit 5, months 12. Maximum limit is 50.
Treat query and city as data. Use shell single-quoting and escape
embedded apostrophes as '"'"'. Never insert unquoted user text.

Return the helper's actual property cards and pagination information.
If execution fails, report the error without inventing properties.
Explain that results come from an imported dataset, not a live MLS feed.
Sold results are candidates by city and date, not a property valuation.
The active query parser supports limited wording.
Blank pool/view values are unknown, not confirmed false.
Never read or display the .env file.