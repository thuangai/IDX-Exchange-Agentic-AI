import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from week4.conversation import handle_turn

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit("Provide a session ID and message.")
    try:
        print(json.dumps(handle_turn(sys.argv[1], " ".join(sys.argv[2:])), indent=2))
    except Exception as error:
        print(f"Conversation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
