"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.handleTurn = handleTurn;
const parse_query_1 = require("../week2/parse_query");
const session_1 = require("./session");
function handleTurn(sessionId, message) {
    const text = message.trim();
    if (!text)
        throw new Error("Please provide a message.");
    if (/^(reset|start over|new search)[.!]?$/i.test(text)) {
        (0, session_1.clearSession)(sessionId);
        return {
            ready: false,
            question: "Which city would you like to search?",
            filters: (0, session_1.getSession)(sessionId).filters,
        };
    }
    const previous = (0, session_1.getSession)(sessionId);
    const parsed = (0, parse_query_1.parsePropertyQuery)(text);
    // Missing fields in this message must not erase earlier preferences.
    const updates = Object.fromEntries(Object.entries(parsed).filter(([, value]) => value !== null));
    // Accept a short city answer when we are waiting for a city.
    if (previous.filters.city === null &&
        parsed.city === null &&
        /^[a-z]+(?:[ -][a-z]+)*$/i.test(text) &&
        !/^(hi|hello|any|no preference)$/i.test(text)) {
        updates.city = text;
    }
    if (/^(any|any type|no preference)[.!]?$/i.test(text)) {
        updates.type = null;
    }
    const session = (0, session_1.updateSession)(sessionId, updates);
    const filters = session.filters;
    let question = null;
    if (filters.city === null) {
        question = "Which city would you like to search?";
    }
    else if (filters.maxPrice === null) {
        question = "What is your maximum budget? For example: under $1.2M.";
    }
    else if (filters.type === null &&
        !session.typePreferenceAnswered) {
        question = "Condo, townhome, single-family, or any type?";
    }
    return {
        ready: question === null,
        question,
        filters,
    };
}
