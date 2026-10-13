import { pool } from "./db";
import { searchActiveListings } from "./search";
import { parsePropertyQuery } from "../week2/parse_query";

async function main() {
  try {
    const query = process.argv.slice(2).join(" ").trim();

    if (!query) {
      throw new Error("Please provide a property search.");
    }

    const filters = parsePropertyQuery(query);
    const result = await searchActiveListings(filters);

    console.log(JSON.stringify({ filters, ...result }, null, 2));
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error("Search failed:", error.message);
  process.exitCode = 1;
});