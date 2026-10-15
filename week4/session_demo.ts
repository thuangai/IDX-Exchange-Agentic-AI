import {
  getSession, updateSession, clearSession,
} from "./session";

const sessionId = "week4-memory-test";
const action = process.argv[2];

if (action === "save") {
  updateSession(sessionId, {
    city: "Irvine",
    maxPrice: 1200000,
  });
} else if (action === "refine") {
  updateSession(sessionId, {
    beds: 3,
    type: "SingleFamilyResidence",
  });
} else if (action === "reset") {
  clearSession(sessionId);
} else if (action !== "show") {
  throw new Error("Use save, refine, show, or reset.");
}

console.log(JSON.stringify(getSession(sessionId), null, 2));