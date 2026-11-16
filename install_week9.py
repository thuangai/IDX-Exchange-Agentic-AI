r"""Windows CMD: .venv\Scripts\python.exe install_week9.py"""
import io
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
REMOTE = r'''
import io, os, shutil, subprocess, sys, tempfile, zipfile
from datetime import datetime, timezone
from pathlib import Path
root = Path.home() / '.openclaw/workspace/idx-exchange-python'
python = root / '.venv/bin/python'
for name in ['.venv/bin/python', 'week3/search.py', 'week5/stats.py', 'week5/trends.py', 'week7/recommend.py', 'week8/rag.py']:
    if not (root / name).is_file():
        raise SystemExit('Missing shared helper: ' + name + '. Install the previous weeks first.')
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
with tempfile.TemporaryDirectory(dir=root, prefix='week9-install-') as temp:
    staging = Path(temp)
    with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as bundle:
        for entry in bundle.infolist():
            if not (staging / entry.filename).resolve().is_relative_to(staging.resolve()):
                raise ValueError('Invalid archive path')
        bundle.extractall(staging)
    # Import previous helpers from the shared installation; candidate week9 from staging.
    environment = dict(os.environ, PYTHONPATH=str(staging) + os.pathsep + str(root))
    subprocess.run([str(python), '-m', 'unittest', 'week9.test_orchestrator', '-v'],
                   cwd=staging, env=environment, check=True)
    week = root / 'week9'
    if week.exists():
        shutil.copytree(week, root / ('week9.before-' + stamp))
    shutil.copytree(staging / 'week9', week, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__'))
    target = root.parent / 'skills/real-estate-orchestrator'
    target.mkdir(parents=True, exist_ok=True)
    current = target / 'SKILL.md'
    if current.exists():
        shutil.copy2(current, target / ('SKILL.md.before-' + stamp))
    temporary = target / 'SKILL.md.tmp'
    shutil.copy2(week / 'SKILL.md', temporary)
    os.replace(temporary, current)
print('Week 9 installed. Start a new OpenClaw chat. Offline routing tests passed; live helpers still need testing.')
'''


def main():
    if sys.platform != 'win32':
        raise SystemExit('Run this installer in Windows Command Prompt.')
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for name in ['__init__.py', 'orchestrator.py', 'test_orchestrator.py', 'SKILL.md', 'README.md']:
            path = ROOT / 'week9' / name
            if not path.is_file():
                raise SystemExit('Missing week9/' + name)
            bundle.write(path, 'week9/' + name)
    try:
        subprocess.run(['wsl', '-d', 'OpenClawGateway', '-u', 'openclaw', '--', 'python3', '-c', REMOTE],
                       input=payload.getvalue(), check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print('Installation failed. Share the error, never credentials.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
