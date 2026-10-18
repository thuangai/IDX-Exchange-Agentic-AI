r"""Run from Windows with .venv\Scripts\python.exe install_week5.py."""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SKILL = '''---
name: market-statistics
description: Answer California real estate market questions using the imported MLS snapshot. Use for median or average sold prices, price per square foot, days on market, list-to-close ratios, active inventory, monthly trends, and questions about whether market conditions favor buyers.
---

Ask for a city if none is supplied. Extract ZIP and property subtype only when requested.
Run the statistics helper and the trends helper to answer a general market question:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week5/stats.py" 'Irvine'
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week5/trends.py" 'Irvine' --json
```

Replace Irvine with the requested city. Shell-quote all arguments safely. Both helpers accept
--zip '92618', --type 'Condominium', --months 12, and --as-of '2026-10-18'.
Use canonical subtype names such as Condominium, Townhouse, or SingleFamilyResidence.
Keep the same filters and as-of date across both calls. Use the default date unless the user requests another.
For a narrow question, run only the helper needed. Never retry successful calls in a loop.

Summarize actual returned values in plain language. For a general overview include median price,
average days on market, average list-to-close percentage, sold count, active snapshot count,
and the available monthly trend. Explain that a ratio of 98% means sales averaged 2% below
their list prices. The ratio uses ListPrice, not OriginalListPrice.

State that the source is an imported snapshot and give the observed sale-date range.
Do not describe the active count as live inventory or treat absent records as proof of zero market sales.
Keep missing values unavailable; never invent year-over-year figures, missing months, or coverage.
Mention that boundary months can be incomplete, especially the first and last observed months.
Describe monthly price changes as changes in the mix of homes sold, not appreciation of the same homes.
For a buyer-timing question, explain the measured indicators and data limits without declaring a
definitive current buy/sell recommendation from this snapshot.
If no sales match, report that and ask whether to broaden the filters.
If execution fails, report the actual error briefly; do not substitute invented results.
Never read or print .env, database passwords, or API keys in a reply.
'''

REMOTE = r'''
import io, os, shutil, subprocess, sys, zipfile
from pathlib import Path

root = Path.home() / '.openclaw' / 'workspace' / 'idx-exchange-python'
python = root / '.venv' / 'bin' / 'python'
if not python.is_file():
    raise SystemExit('The shared Python installation is missing. Run install_openclaw.py first.')
with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as bundle:
    for entry in bundle.infolist():
        destination = (root / entry.filename).resolve()
        if not destination.is_relative_to(root.resolve()):
            raise ValueError('Invalid archive path')
    bundle.extractall(root)
# Verify imports, MySQL access, and both helpers before making the skill discoverable.
subprocess.run([str(python), str(root / 'week5' / 'stats.py'), 'Irvine'], check=True)
subprocess.run([str(python), str(root / 'week5' / 'trends.py'), 'Irvine'], check=True)
target = root.parent / 'skills' / 'market-statistics'
target.mkdir(parents=True, exist_ok=True)
current = target / 'SKILL.md'
if current.exists():
    shutil.copy2(current, target / 'SKILL.md.before-week5')
temporary = target / 'SKILL.md.tmp'
shutil.copy2(root / 'week5' / 'SKILL.md', temporary)
os.replace(temporary, current)
print('\nWeek 5 installed: market-statistics. Start a new OpenClaw chat to test it.')
'''


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run this installer in Windows CMD, not Ubuntu.')
    files = ['week5/stats.py', 'week5/trends.py', 'week3/db.py']
    for name in files:
        if not (ROOT / name).is_file():
            raise SystemExit(f'Missing {name}. Keep this installer in the project root.')
    # Keep the skill instructions in the project so they can be reviewed and committed.
    skill_path = ROOT / 'week5' / 'SKILL.md'
    skill_path.write_text(SKILL, encoding='utf-8')
    init_path = ROOT / 'week5' / '__init__.py'
    if not init_path.exists():
        init_path.write_text('', encoding='utf-8')
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name in files + ['week5/SKILL.md', 'week5/__init__.py']:
            bundle.write(ROOT / name, name)
    try:
        subprocess.run(['wsl', '-d', 'OpenClawGateway', '-u', 'openclaw', '--',
                        'python3', '-c', REMOTE], input=payload.getvalue(), check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('Installation did not finish. Share the error output, never your .env.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
