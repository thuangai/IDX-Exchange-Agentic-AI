"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const conversation_1 = require("./conversation");
const db_1 = require("../week3/db");
const search_1 = require("../week3/search");
const format_1 = require("../week3/format");
async function main() {
    try {
        const [sessionId, ...words] = process.argv.slice(2);
        if (!sessionId || words.length === 0) {
            throw new Error("Provide a session ID and message.");
        }
        const turn = (0, conversation_1.handleTurn)(sessionId, words.join(" "));
        if (!turn.ready) {
            console.log(turn.question);
            return;
        }
        const result = await (0, search_1.searchActiveListings)(turn.filters, 1, 5);
        console.log("Searching with these saved preferences:");
        console.log(JSON.stringify(turn.filters, null, 2));
        console.log("\nSource: imported MLS dataset\n");
        console.log((0, format_1.formatCards)(result.properties, "active"));
        console.log(`\nMore results available: ${result.hasMore}`);
        console.log("You can change your preferences or say 'start over'.");
    }
    finally {
        await db_1.pool.end();
    }
}
main().catch((error) => {
    console.error("Conversation failed:", error.message);
    process.exitCode = 1;
});
