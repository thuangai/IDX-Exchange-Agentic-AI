# Week 9: Multi-Agent Orchestration

One Python/OpenClaw entry point coordinates the existing Week 3 property search,
Week 5 statistics and trends, Week 7 recommendations, Week 8 cited RAG, and a new
plain-text email draft formatter. Independent agents execute concurrently using
separate helper calls; email composition waits for evidence. No email is sent.

## Install on your PC

Extract this update ZIP into `C:\Users\Huy\OneDrive\Documents\A__idx`.
It adds `week9` and `install_week9.py`; keep the existing project and private settings.
With the previous weeks installed, run in **Windows Command Prompt**:

```cmd
.venv\Scripts\python.exe -m unittest week9.test_orchestrator -v
.venv\Scripts\python.exe install_week9.py
```

The installer targets **OpenClawGateway** as **openclaw**, backs up any existing
Week 9 code/skill, and tests the candidate before enabling the skill. It does not
reinstall packages, change previous skills, copy credentials, or rebuild indexes.
No new dependencies. Start a new OpenClaw chat after installation.

## Local command examples (Windows CMD)

```cmd
.venv\Scripts\python.exe week9\orchestrator.py demo "Find condos in Irvine under $900k"
.venv\Scripts\python.exe week9\orchestrator.py demo "Under $850k"
.venv\Scripts\python.exe week9\orchestrator.py demo "Recommend similar homes"
.venv\Scripts\python.exe week9\orchestrator.py demo "Show market trends in Irvine"
.venv\Scripts\python.exe week9\orchestrator.py demo "What is DOM? Cite your sources."
.venv\Scripts\python.exe week9\orchestrator.py demo "Draft an email with that summary"
.venv\Scripts\python.exe week9\orchestrator.py demo "Find homes in Pasadena and tell me whether prices are rising"
.venv\Scripts\python.exe week9\orchestrator.py demo "Start over"
```

`demo` is for local testing only; use distinct trusted IDs for real conversations.
Local Windows commands need the existing Windows database settings, API key,
Week 6 recommendation index, and Week 8 sources/index. The installed OpenClaw
version reuses its own previously tested Linux setup. Run MySQL as before.

Inspect routing with `--plan` without database/API calls. For unsupported wording,
use `--city "Irvine"`, `--listing-id 1182905312`, or `--agents marketStatsAgent`.
The explicit agent option accepts multiple names. Supported names are
propertySearchAgent, marketStatsAgent, recommendationAgent, ragAgent, emailDraftAgent.
The CLI defaults to 12 months and today's reporting date; use `--months 6` or
`--as-of 2026-11-01` for a deliberate reporting window. Missing matches remain
missing data; the coordinator never shifts dates automatically.

## Behavior and limitations

Routing is a transparent regex baseline, not a general language understanding
model. OpenClaw can supply explicit agent/city hints from the actual request.
The original Week 2 parser's supported filters are unchanged: wording such as
"affordable" without a numeric budget does not impose a price ceiling. Check
intent and filters rather than assuming every phrase is understood.

Successful searches save the first listing as the default reference for a later
recommendation. An explicit listing ID overrides it. Search preferences and
last successful evidence persist under a separate hashed Week 9 session directory
(`IDX_WEEK9_SESSION_DIR` overrides it). Use `start over` to remove that session.
Calls must be sequential per session. Different sessions are isolated. Local
session files do not expire automatically.

Results include per-agent success, clarification, or error status. Partial results
remain available; raw exception text is hidden to avoid exposing credentials.
Drafts preserve the structured evidence and citations in a plain-text template;
they are not polished natural-language sales copy. An email-only follow-up uses
saved evidence. A fresh request that fails never silently uses older evidence.
All current sources are imported snapshots, not live inventory or a forecast.

## Validation and completion

Offline tests cover all five routes, mixed parallel dispatch, session refinement,
reference reuse, isolation/reset, missing inputs, preserved citations, safe partial
failure, explicit hints, and grounded email drafting. They use fake agent outputs;
they do not establish MySQL/API/WhatsApp availability.

After installing, test each of the example requests in a new OpenClaw chat using
`real-estate-orchestrator`. Verify the returned `agents` and each result's status,
check real values against the original helper, and test one mixed request. Also
repeat a search + follow-up + recommendation through WhatsApp with its own ID.
Week 9's live demonstration is complete only after those checks pass on your PC.
