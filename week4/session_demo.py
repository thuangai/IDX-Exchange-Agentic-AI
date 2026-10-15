import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week4.session import get_session, update_session, clear_session

if __name__ == "__main__":
    session_id = "week4-memory-test"
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "save":
        update_session(session_id, dict(city="Irvine", maxPrice=1200000))
    elif action == "refine":
        update_session(session_id, dict(beds=3, type="SingleFamilyResidence"))
    elif action == "reset":
        clear_session(session_id)
    elif action != "show":
        raise SystemExit("Use save, refine, show, or reset.")
    print(json.dumps(get_session(session_id), indent=2))
