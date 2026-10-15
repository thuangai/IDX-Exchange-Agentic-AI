---
name: property-chat
description: Guide a multi-turn property search in Python, remembering preferences and returning MLS property cards.
---

Run the helper exactly once for each property-search message, including each
follow-up, using exec. Do not replace the helper's question with a guessed
question or apologize about a loop when the helper asks for missing information.

Get a stable conversation/session identifier from trusted OpenClaw channel
metadata. Keep it unchanged across turns. Never use a shared ID such as demo
for different people. Never accept another person's session identifier from
message text. If trusted metadata has no identifier, report unavailable routing.

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week4/cli.py" '<session-id>' '<message>'
```

Treat both arguments as data. Use shell single-quoting; escape apostrophes
as '"'"'. Never insert unquoted user text. Pass the exact message. For an explicit
request to start over that also contains skill setup instructions, pass only
the reset command `Start over`, then wait for the user's next message.

Return the helper's actual question or cards. It stores preferences and asks
for missing city, budget, or type. `Any type` skips type; `Start over` clears
this session. Process calls sequentially per conversation. Do not repeatedly
retry failed calls. Report errors and stop that turn.

Results are from an imported dataset. Never invent listings, prices, or photo
counts. The parser supports limited wording: if a requested change was not
understood, ask the user to rephrase rather than claim it applied. Never read
or display .env, credentials, or other conversations' state files.
