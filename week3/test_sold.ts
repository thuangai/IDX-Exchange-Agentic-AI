import { pool } from "./db";
import { getSoldComps } from "./sold";

async function main() {
  try {
    const city = process.argv[2] ?? "Irvine";
    const months = Number(process.argv[3] ?? 12);
    const result = await getSoldComps(city, months);

    console.log(JSON.stringify(result, null, 2));
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error("Sold search failed:", error.message);
  process.exitCode = 1;
});