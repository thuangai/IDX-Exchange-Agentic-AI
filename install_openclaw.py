"""Run on Windows: py install_openclaw.py. No PowerShell copy commands needed."""
import io
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# This code runs inside OpenClawGateway. Only the curated bundle is extracted.
REMOTE_INSTALL = r'''
import io, os, shutil, subprocess, sys, zipfile
from pathlib import Path

root = Path.home() / '.openclaw' / 'workspace' / 'idx-exchange-python'
root.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())) as bundle:
    for entry in bundle.infolist():
        destination = (root / entry.filename).resolve()
        if not destination.is_relative_to(root.resolve()):
            raise ValueError('Invalid archive path')
        if entry.filename == '.env':
            destination.unlink(missing_ok=True)
        bundle.extract(entry, root)
os.chmod(root / '.env', 0o600)
venv = root / '.venv'
if not (venv / 'bin' / 'python').exists():
    subprocess.run([sys.executable, '-m', 'venv', str(venv)], check=True)
python = venv / 'bin' / 'python'
subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.txt')], check=True)
subprocess.run([str(python), str(root / 'week2' / 'test_queries.py')], check=True)
subprocess.run([str(python), str(root / 'week3' / 'test_db.py')], check=True)
# Switch the three existing skills only after dependencies and MySQL work.
skills = root.parent / 'skills'
for week, name in [('week2', 'property-query'), ('week3', 'mls-search'), ('week4', 'property-chat')]:
    target = skills / name
    target.mkdir(parents=True, exist_ok=True)
    current = target / 'SKILL.md'
    backup = target / 'SKILL.md.before-python'
    if current.exists() and not backup.exists():
        shutil.copy2(current, backup)
    shutil.copy2(root / week / 'SKILL.md', current)
print('Python helpers installed. Start a new OpenClaw chat and test property-chat.')
'''


def main():
    if sys.platform != "win32":
        raise SystemExit("Run this installer on your Windows PC, not in Ubuntu.")
    env_path = next((p for p in (ROOT / "week3" / ".env", ROOT / ".env") if p.is_file()), None)
    if env_path is None:
        raise SystemExit("Keep your existing week3/.env, or create .env from .env.example first.")
    payload = io.BytesIO()
    with zipfile.ZipFile(payload, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(ROOT / "requirements.txt", "requirements.txt")
        for week in ("week2", "week3", "week4"):
            for file in (ROOT / week).iterdir():
                if file.is_file() and (file.suffix == ".py" or file.name in ("SKILL.md", "README.md")):
                    bundle.write(file, f"{week}/{file.name}")
        # Transfer directly to your own WSL installation; never print this file.
        bundle.write(env_path, ".env")
    try:
        subprocess.run(
            ["wsl", "-d", "OpenClawGateway", "-u", "openclaw", "--", "python3", "-c", REMOTE_INSTALL],
            input=payload.getvalue(), check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installation did not finish. Keep the old code and share the error, not your .env.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
