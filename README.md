# IDX Exchange Agentic AI — Python

Internship work rewritten from TypeScript into readable Python 3.10+.
Week 1's architecture PDF is unchanged. No Node.js or build step is needed.

| Folder | Purpose |
| --- | --- |
| `week2` | Parse a property-search sentence into filters |
| `week3` | Query MySQL active/sold tables and format property cards |
| `week4` | Remember preferences, ask follow-ups, and refine searches |
| `tests` | Offline regression tests using synthetic data |

## Start on Windows

Open **Command Prompt** (`C:\...>`). These commands run from the project root:

```cmd
cd /d C:\Users\Huy\OneDrive\Documents\A__idx
py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe week2\test_queries.py
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

If `.venv` already exists, reuse it if it has a Windows `Scripts/python.exe`.
If `py` is unavailable but Windows `python --version` reports 3.10 or later,
use `python` instead of `py`. No PowerShell activation is required.

Keep the existing `week3/.env`. If it is missing, copy `.env.example` to
`week3/.env` and enter your local MySQL password privately.
The database loader finds this file from any working directory. Alternatively
use a root `.env`, or set `IDX_ENV_FILE` to an explicit path. Existing environment
variables take priority over file values.

In a **separate terminal**, start Ubuntu and keep that window open:

```cmd
wsl -d Ubuntu
```

Inside Ubuntu (`huy@...`):

```bash
sudo service mysql start
```

Back in **Windows Command Prompt**, run:

```cmd
.venv\Scripts\python.exe week3\test_db.py
.venv\Scripts\python.exe week3\cli.py active "Condos in Irvine under $900k" 1 5
.venv\Scripts\python.exe week3\cli.py sold Irvine 1 5 12
.venv\Scripts\python.exe week4\cli.py demo "Start over"
.venv\Scripts\python.exe week4\cli.py demo "Find homes in Irvine"
.venv\Scripts\python.exe week4\cli.py demo "Under $1.2M"
.venv\Scripts\python.exe week4\cli.py demo "Single family with at least 3 beds"
.venv\Scripts\python.exe week4\cli.py demo "Under $1.5M"
```

Use double quotes in Command Prompt. In PowerShell and Linux, use single quotes
around searches containing `$` so the shell does not expand the budget.

## Update OpenClaw

With Ubuntu/MySQL running, run on Windows:

```cmd
.venv\Scripts\python.exe install_openclaw.py
```

The installer sends the Python helpers and your local database settings directly
to your own `OpenClawGateway` distro. It does not upload credentials to GitHub.
It creates a Linux virtual environment, installs dependencies, and checks MySQL
before replacing the three existing skill instructions. Old instructions are
backed up as `SKILL.md.before-python`. Re-running the installer refreshes the
Python helpers after edits.

If Linux reports that `venv`/`ensurepip` is unavailable, install `python3-venv`
inside **OpenClawGateway** using its root account, then rerun the installer:

```cmd
wsl -d OpenClawGateway -u root -- apt-get update
wsl -d OpenClawGateway -u root -- apt-get install -y python3-venv
```

Start a new OpenClaw chat and test `property-query`, `mls-search`, and
`property-chat`. Then repeat the property-chat conversation through WhatsApp.
MySQL, the SQL tables, WhatsApp pairing, and your model API configuration remain
in place. Model calls still depend on the provider's quota.

## Finish replacing TypeScript

See `MIGRATION.md`. The ZIP contains the Python project and Week 1 PDF, but no
`.git`, credentials, company SQL data, Node dependencies, or compiled JS.
Extracting it over your project adds/replaces files; it does not delete old files.
Keep your existing `.git` folder and `week3/.env`.

## Verification and limits

The original ten parser cases and offline regression tests are included.
`tests` executes generated queries against synthetic SQLite tables; this is
not a substitute for the real MySQL connection test. The migration report records
the checks run during conversion. Live MySQL and WhatsApp must be retested on
your PC after installation.

The parser is intentionally a port of the current regex implementation, not a
general language model. Unsupported wording may be ignored. Blank pool/view
values are unknown. Sold comparisons use city/date rather than valuation logic.
Results come from an imported dataset, not a live MLS feed. Conversation turns
must be sequential for each session; session files do not expire automatically.
