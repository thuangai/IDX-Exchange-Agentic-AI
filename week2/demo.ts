import { parsePropertyQuery } from "./parse_query";

const query = "Show me 3-bedroom condos in Irvine under $1.5M with a pool.";
console.log(JSON.stringify(parsePropertyQuery(query), null, 2));