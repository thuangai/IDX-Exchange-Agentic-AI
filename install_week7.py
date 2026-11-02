r"""Run in Windows CMD: .venv\Scripts\python.exe install_week7.py"""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = '''---
name: property-recommendations
description: Recommend the top five active properties similar to a listing the user likes, combining structured and embedding scores with recent sold-comparable price assessments. Use when given a reference listing ID and asked for similar homes or alternatives.
---

Ask for the reference listing ID if it is not provided. Run this helper once, safely quoting the ID:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week7/recommend.py" '1182905312'
```

Replace the example ID with the user's listing ID. Use --as-of YYYY-MM-DD only when requested.
Use the actual helper output, not remembered results. The helper reuses cached Gemini vectors and makes no embedding API requests.
Summarize the reference property and state indexed_candidates_scored. Present up to five returned recommendations,
ordered exactly as returned, using bullets or correctly numbered items 1 through 5.
For each include address, listing ID, type, asking price, beds, baths, square footage,
total score, and a short explanation from structured_breakdown and cosine_similarity.
The score is up to 60 structured points plus 40 times cosine similarity, not a probability.
Property type and bathrooms are displayed but not components of the handbook's structured score;
do not claim every recommendation has the same type or bathroom count as the reference.

Include each recommendation's comp_count, comp_based_price, difference_pct, and observed comparable date range.
Positive difference_pct means asking above the baseline; negative means below. Explain this clearly.
If assessment is limited_sample, mention the small sample. If unavailable, say why and do not invent a value.
The baseline uses average sold price per square foot times the candidate's area, matching city and known subtype,
within +/-20% area and the prior six calendar months, excluding future dates.
Call it a sold-comparable baseline, never an appraisal, fair-value guarantee, or proof a home is underpriced.
Do not claim all six months have complete records. Report the actual first and last comparable dates.
State that results cover fresh indexed active listings within an imported snapshot, not live MLS availability.
The initial index covers Irvine. Never silently expand an index or generate embeddings.
If execution fails, briefly report the error; do not loop, invent listings, or print private settings.
'''

REMOTE = r'''
import io, os, shutil, subprocess, sys, zipfile
from pathlib import Path
root = Path.home() / '.openclaw' / 'workspace' / 'idx-exchange-python'
python = root / '.venv' / 'bin' / 'python'
for required in [python, root / 'week6/semantic.py', root / 'data/week6-semantic.sqlite']:
    if not required.is_file():
        raise SystemExit('Week 6 shared setup or index missing. Run install_week6.py first.')
with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as bundle:
    for entry in bundle.infolist():
        if not (root / entry.filename).resolve().is_relative_to(root.resolve()):
            raise ValueError('Invalid archive path')
    bundle.extractall(root)
# Verify the helper against the installed database and index before enabling the skill.
subprocess.run([str(python), str(root / 'week7/recommend.py'), '1182905312'], check=True)
target = root.parent / 'skills' / 'property-recommendations'
target.mkdir(parents=True, exist_ok=True)
current = target / 'SKILL.md'
if current.exists():
    shutil.copy2(current, target / 'SKILL.md.before-week7')
temporary = target / 'SKILL.md.tmp'
shutil.copy2(root / 'week7/SKILL.md', temporary)
os.replace(temporary, current)
print('\nWeek 7 installed: property-recommendations. Start a new OpenClaw chat to test it.')
'''


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run this installer in Windows CMD, not Ubuntu.')
    if not (ROOT / 'week7/recommend.py').is_file():
        raise SystemExit('Missing week7/recommend.py. Keep this installer in the project root.')
    (ROOT / 'week7/SKILL.md').write_text(SKILL, encoding='utf-8')
    (ROOT / 'week7/__init__.py').touch(exist_ok=True)
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name in ['week7/recommend.py', 'week7/SKILL.md', 'week7/__init__.py']:
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
