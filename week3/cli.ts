import { pool } from "./db";
import { searchActiveListings } from "./search";
import { getSoldComps } from "./sold";
import { formatCards } from "./format";
import { parsePropertyQuery } from "../week2/parse_query";

async function main() {
  try {
    const [mode, input, pageArg, limitArg, monthsArg] =
      process.argv.slice(2);

    if (!input || (mode !== "active" && mode !== "sold")) {
      throw new Error(
        "Usage: cli.ts active 'query' [page] [limit]\n" +
        "       cli.ts sold 'city' [page] [limit] [months]"
      );
    }

    const page = Number(pageArg ?? 1);
    const limit = Number(limitArg ?? 5);

    const result = mode === "active"
      ? await searchActiveListings(
          parsePropertyQuery(input), page, limit
        )
      : await getSoldComps(
          input, Number(monthsArg ?? 12), page, limit
        );

    console.log(`Source: imported MLS dataset | Page ${result.page}`);
    if ("asOf" in result && "months" in result) {
      console.log(`Sales window: ${result.months} months through ${result.asOf}`);
    }

    console.log();
    console.log(formatCards(result.properties, mode));
    console.log(`\nMore results available: ${result.hasMore}`);
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error("Search failed:", error.message);
  process.exitCode = 1;
});