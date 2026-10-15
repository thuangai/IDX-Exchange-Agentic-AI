import { handleTurn } from "./conversation";
import { pool } from "../week3/db";
import { searchActiveListings } from "../week3/search";
import { formatCards } from "../week3/format";

async function main() {
  try {
    const [sessionId, ...words] = process.argv.slice(2);

    if (!sessionId || words.length === 0) {
      throw new Error("Provide a session ID and message.");
    }

    const turn = handleTurn(sessionId, words.join(" "));

    if (!turn.ready) {
      console.log(turn.question);
      return;
    }

    const result = await searchActiveListings(turn.filters, 1, 5);

    console.log("Searching with these saved preferences:");
    console.log(JSON.stringify(turn.filters, null, 2));
    console.log("\nSource: imported MLS dataset\n");
    console.log(formatCards(result.properties, "active"));
    console.log(`\nMore results available: ${result.hasMore}`);
    console.log("You can change your preferences or say 'start over'.");
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error("Conversation failed:", error.message);
  process.exitCode = 1;
});