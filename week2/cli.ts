import { parsePropertyQuery } from "./parse_query";

const query = process.argv.slice(2).join(" ").trim();

if (!query) {
  console.error("Please provide a property-search query.");
  process.exit(1);
}

console.log(JSON.stringify(parsePropertyQuery(query), null, 2));