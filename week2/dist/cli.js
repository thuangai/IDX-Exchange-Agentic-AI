"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const parse_query_1 = require("./parse_query");
const query = process.argv.slice(2).join(" ").trim();
if (!query) {
    console.error("Please provide a property-search query.");
    process.exit(1);
}
console.log(JSON.stringify((0, parse_query_1.parsePropertyQuery)(query), null, 2));
