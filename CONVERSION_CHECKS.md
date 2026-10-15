# Conversion checks

Source: `thuangai/IDX-Exchange-Agentic-AI`, commit `8258cff`.
Runtime used here: Python 3.12.14, Node 24.19.0 for comparisons only.
Installed Python dependencies: mysql-connector-python 9.7.0, python-dotenv 1.2.4.

Completed during conversion:

- Original Week 2 query cases: **10/10 passed**.
- Parser parity: **30/30** search outputs matched the repository's original
  compiled TypeScript parser, including the ten original queries and additional
  budget, HOA, feature, city, and bedroom/bath examples.
- Conversation parity: **15/15** turn outputs matched the original compiled
  TypeScript helper, covering reset, missing preferences, type selection,
  budget refinement, pool changes, multiple sessions, and any-type handling.
- Offline regression suite: **16 test methods passed**, including subcases.
- Generated active and sold SELECTs executed on synthetic SQLite fixtures.
  The fixture adapter substitutes the connector's value placeholders; it does
  not replace MySQL syntax or simulate the actual Connector/Python transport.
- Connector cleanup checked with a mock on successful and failed queries.
- Decimal JSON/cards and photo-count formatting checked.
- Session persistence verified across separate Python processes.
- Existing TypeScript-format JSON session read by Python.
- `git diff --check` passed.

Remaining checks on the user's PC:

- Install Python dependencies in Windows and OpenClawGateway virtual environments.
- Run `week3/test_db.py` against the real MySQL server and confirm counts.
- Compare real active and sold searches, including page 2.
- Run `install_openclaw.py`; test each refreshed skill.
- Repeat the full WhatsApp city/budget/type/refinement conversation.

No live MySQL, model/API calls, Windows/WSL deployment, or WhatsApp integration
was tested in this conversion environment. No code was pushed to GitHub.
