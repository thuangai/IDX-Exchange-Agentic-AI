# Week 4: Conversational Property Search (Python)

`conversation.py` asks follow-up questions and merges new preferences into
saved filters. `session.py` stores JSON state between calls. `cli.py` searches
the Week 3 database when enough preferences are known.

From the project root in Windows Command Prompt:

```cmd
.venv\Scripts\python.exe week4\conversation_demo.py demo "Start over"
.venv\Scripts\python.exe week4\conversation_demo.py demo "Find homes in Irvine"
.venv\Scripts\python.exe week4\conversation_demo.py demo "Under $1.2M"
.venv\Scripts\python.exe week4\conversation_demo.py demo "Single family with at least 3 beds"
```

The demo prints state without needing MySQL. To return actual property cards,
run `week4\cli.py` with the same arguments after starting MySQL.

```cmd
.venv\Scripts\python.exe week4\cli.py demo "Under $1.5M"
```

That keeps Irvine, single-family, and 3 bedrooms while updating the budget.
`Any type` clears the type filter and prevents another type question.
An exact `Start over`, `reset`, or `new search` resets the current session.

Session files retain the original path and SHA-256 filenames:
`~/.idx-exchange/week4-sessions/`. Existing TypeScript session files are read
by Python on the same operating-system account. Windows and OpenClaw's Linux
account have separate home folders and therefore separate state. Tests can
override the location using `IDX_SESSION_DIR`.

OpenClaw must supply a trusted, stable session ID; `demo` is only for local
testing. Calls per conversation must be sequential. State does not expire
automatically. No API calls are made by the Python parser itself.

Run `install_openclaw.py` from Windows to refresh the `property-chat` skill.
Repeat the city/budget/type/refinement conversation in WhatsApp after migration.
The old TypeScript version's WhatsApp test does not prove the new Python
installation is connected correctly.
