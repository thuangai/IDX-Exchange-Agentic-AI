import { pool } from "./db";

async function main() {
  try {
    const [rows] = await pool.execute(`
      SELECT
        DATABASE() AS database_name,
        (SELECT COUNT(*) FROM rets_property) AS active_listings,
        (SELECT COUNT(*) FROM california_sold) AS sold_properties
    `);

    console.table(rows);
    console.log("MySQL connection successful!");
  } finally {
    await pool.end();
  }
}

main().catch((error) => {
  console.error("Connection failed:", error.message);
  process.exitCode = 1;
});