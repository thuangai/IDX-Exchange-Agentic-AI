"""Compatible with the existing TypeScript JSON sessions. Run turns sequentially."""
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from week2.parse_query import empty_filters


def session_path(session_id):
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("A session ID is required.")
    directory = Path(os.environ.get(
        "IDX_SESSION_DIR", str(Path.home() / ".idx-exchange" / "week4-sessions")
    )).expanduser()
    filename = hashlib.sha256(session_id.encode("utf-8")).hexdigest() + ".json"
    return directory / filename


def now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def get_session(session_id):
    path = session_path(session_id)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("filters"), dict):
            raise ValueError("Saved session is invalid. Start over to reset it.")
        data["filters"] = {**empty_filters(), **data["filters"]}
        return data
    return dict(filters=empty_filters(), page=1, updatedAt=now())


def update_session(session_id, updates):
    if set(updates) - set(empty_filters()):
        raise ValueError("Unknown preference field.")
    session = get_session(session_id)
    next_session = dict(
        filters={**session["filters"], **updates}, page=1, updatedAt=now(),
        typePreferenceAnswered=bool(session.get("typePreferenceAnswered") or "type" in updates),
    )
    path = session_path(session_id)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(next_session, stream, indent=2)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)
    return next_session


def clear_session(session_id):
    session_path(session_id).unlink(missing_ok=True)
