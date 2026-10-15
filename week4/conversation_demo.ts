import { handleTurn } from "./conversation";

const [sessionId, ...words] = process.argv.slice(2);

if (!sessionId) {
  throw new Error("Provide a session ID and message.");
}

const result = handleTurn(sessionId, words.join(" "));
console.log(JSON.stringify(result, null, 2));