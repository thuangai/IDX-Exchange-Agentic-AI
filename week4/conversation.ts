import { parsePropertyQuery } from "../week2/parse_query";
import {
  getSession, updateSession, clearSession,
} from "./session";

export function handleTurn(sessionId: string, message: string) {
  const text = message.trim();
  if (!text) throw new Error("Please provide a message.");

  if (/^(reset|start over|new search)[.!]?$/i.test(text)) {
    clearSession(sessionId);
    return {
      ready: false,
      question: "Which city would you like to search?",
      filters: getSession(sessionId).filters,
    };
  }

  const previous = getSession(sessionId);
  const parsed = parsePropertyQuery(text);

  // Missing fields in this message must not erase earlier preferences.
  const updates = Object.fromEntries(
    Object.entries(parsed).filter(([, value]) => value !== null)
  ) as Partial<typeof parsed>;

  // Accept a short city answer when we are waiting for a city.
  if (
    previous.filters.city === null &&
    parsed.city === null &&
    /^[a-z]+(?:[ -][a-z]+)*$/i.test(text) &&
    !/^(hi|hello|any|no preference)$/i.test(text)
  ) {
    updates.city = text;
  }

  if (/^(any|any type|no preference)[.!]?$/i.test(text)) {
    updates.type = null;
  }

  const session = updateSession(sessionId, updates);
  const filters = session.filters;

  let question: string | null = null;

  if (filters.city === null) {
    question = "Which city would you like to search?";
  } else if (filters.maxPrice === null) {
    question = "What is your maximum budget? For example: under $1.2M.";
  } else if (
    filters.type === null &&
    !session.typePreferenceAnswered
  ) {
    question = "Condo, townhome, single-family, or any type?";
  }

  return {
    ready: question === null,
    question,
    filters,
  };
}