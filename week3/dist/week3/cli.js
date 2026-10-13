"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const db_1 = require("./db");
const search_1 = require("./search");
const sold_1 = require("./sold");
const format_1 = require("./format");
const parse_query_1 = require("../week2/parse_query");
async function main() {
    try {
        const [mode, input, pageArg, limitArg, monthsArg] = process.argv.slice(2);
        if (!input || (mode !== "active" && mode !== "sold")) {
            throw new Error("Usage: cli.ts active 'query' [page] [limit]\n" +
                "       cli.ts sold 'city' [page] [limit] [months]");
        }
        const page = Number(pageArg ?? 1);
        const limit = Number(limitArg ?? 5);
        const result = mode === "active"
            ? await (0, search_1.searchActiveListings)((0, parse_query_1.parsePropertyQuery)(input), page, limit)
            : await (0, sold_1.getSoldComps)(input, Number(monthsArg ?? 12), page, limit);
        console.log(`Source: imported MLS dataset | Page ${result.page}`);
        if ("asOf" in result && "months" in result) {
            console.log(`Sales window: ${result.months} months through ${result.asOf}`);
        }
        console.log();
        console.log((0, format_1.formatCards)(result.properties, mode));
        console.log(`\nMore results available: ${result.hasMore}`);
    }
    finally {
        await db_1.pool.end();
    }
}
main().catch((error) => {
    console.error("Search failed:", error.message);
    process.exitCode = 1;
});
