"""Remove the named Node source/build files only after testing Python locally."""
import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = {
    "week2": ["cli", "demo", "parse_query", "test_queries"],
    "week3": ["cli", "db", "format", "search", "sold", "test_db", "test_search", "test_sold"],
    "week4": ["cli", "conversation", "conversation_demo", "session", "session_demo"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove-old", action="store_true", help="Delete the old TypeScript and build files")
    args = parser.parse_args()
    targets = []
    for week, names in FILES.items():
        for name in names:
            if not (ROOT / week / f"{name}.py").is_file():
                raise SystemExit(f"Missing replacement: {week}/{name}.py")
            targets.append(ROOT / week / f"{name}.ts")
        targets.extend(ROOT / week / name for name in ("dist", "package.json", "package-lock.json"))
    for path in targets:
        if path.exists():
            print(("Removing: " if args.remove_old else "Would remove: ") + str(path.relative_to(ROOT)))
            if args.remove_old:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
    if not args.remove_old:
        print("After the Python/MySQL/OpenClaw checks pass, run: py finish_migration.py --remove-old")


if __name__ == "__main__":
    main()
