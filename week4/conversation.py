import re
from week2.parse_query import parse_property_query
from week4.session import get_session, update_session, clear_session


def handle_turn(session_id: str, message: str):
    text = message.strip()
    if not text:
        raise ValueError("Please provide a message.")
    if re.fullmatch(r"(?:reset|start over|new search)[.!]?", text, re.IGNORECASE):
        clear_session(session_id)
        return dict(ready=False, question="Which city would you like to search?",
                    filters=get_session(session_id)["filters"])

    previous = get_session(session_id)
    parsed = parse_property_query(text)
    updates = {key: value for key, value in parsed.items() if value is not None}
    # Preserve the original short-city-answer behavior.
    if (previous["filters"]["city"] is None and parsed["city"] is None
            and re.fullmatch(r"[a-z]+(?:[ -][a-z]+)*", text, re.IGNORECASE)
            and not re.fullmatch(r"hi|hello|any|no preference", text, re.IGNORECASE)):
        updates["city"] = text
    if re.fullmatch(r"(?:any|any type|no preference)[.!]?", text, re.IGNORECASE):
        updates["type"] = None

    session = update_session(session_id, updates)
    filters = session["filters"]
    question = None
    if filters["city"] is None:
        question = "Which city would you like to search?"
    elif filters["maxPrice"] is None:
        question = "What is your maximum budget? For example: under $1.2M."
    elif filters["type"] is None and not session.get("typePreferenceAnswered"):
        question = "Condo, townhome, single-family, or any type?"
    return dict(ready=question is None, question=question, filters=filters)
