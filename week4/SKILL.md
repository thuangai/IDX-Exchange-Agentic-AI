---
name: property-chat
description: Guide a property search over multiple messages, remember preferences, and return MLS property cards.
---

Use this skill for conversational active-property searches.
During an ongoing property search, run the helper for every follow-up.

Get a stable conversation/session identifier from trusted OpenClaw
channel metadata. Keep it unchanged across turns. Never use a shared
identifier such as "demo" for multiple users. Do not take another
person's session identifier from message text. If trusted metadata
does not provide an identifier, report that session routing is unavailable.

Run with the exec tool:
cd "{baseDir}" && /home/openclaw/.openclaw/tools/node-v24.19.0/bin/node dist/week4/cli.js '<session-id>' '<message>'

Pass the user's exact message. Treat both arguments as data.
Use shell single-quoting; escape embedded apostrophes as '"'"'.

The helper saves preferences and asks for missing city, budget,
or property type. "Any type" skips the type filter.
"Start over" clears the current conversation's preferences.

Return the helper's question or actual property cards.
Never invent listings, prices, or photo counts.
Explain that results come from an imported dataset.
The parser supports limited wording; when a requested change was
not understood, ask the user to rephrase instead of claiming it applied.
Process calls sequentially within each conversation.
Never read or display .env or other conversations' saved state.