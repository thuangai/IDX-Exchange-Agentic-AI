"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getSoldComps = getSoldComps;
const db_1 = require("./db");
async function getSoldComps(city, months = 12, page = 1, limit = 5, asOf = new Date().toISOString().slice(0, 10)) {
    if (!city.trim()) {
        throw new Error("Please provide a city.");
    }
    if (!Number.isInteger(months) || months < 1 || months > 120) {
        throw new Error("Months must be between 1 and 120.");
    }
    if (!Number.isSafeInteger(page) || page < 1) {
        throw new Error("Page must be a positive integer.");
    }
    if (!Number.isInteger(limit) || limit < 1 || limit > 50) {
        throw new Error("Limit must be between 1 and 50.");
    }
    const parsedDate = new Date(`${asOf}T00:00:00Z`);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(asOf) ||
        !Number.isFinite(parsedDate.getTime()) ||
        parsedDate.toISOString().slice(0, 10) !== asOf) {
        throw new Error("asOf must be a valid YYYY-MM-DD date.");
    }
    const offset = (page - 1) * limit;
    if (!Number.isSafeInteger(offset)) {
        throw new Error("Page is too large.");
    }
    // CloseDate is text in this dataset.
    // YYYY-MM-DD strings can be compared in chronological order.
    const sql = `
    SELECT
      CAST(ListingKey AS CHAR) AS listingId,
      UnparsedAddress AS address,
      City AS city,
      CloseDate AS closeDate,
      ClosePrice AS price,
      BedroomsTotal AS beds,
      BathroomsTotalInteger AS baths,
      LivingArea AS sqft,
      PropertySubType AS type,
      DaysOnMarket AS daysOnMarket
    FROM california_sold
    WHERE City = ?
      AND PropertyType = ?
      AND CloseDate REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'
      AND CloseDate >= DATE_FORMAT(
        DATE_SUB(CAST(? AS DATE), INTERVAL ? MONTH), '%Y-%m-%d'
      )
      AND CloseDate <= ?
      AND ClosePrice > 0
    ORDER BY CloseDate DESC, ListingKey DESC
    LIMIT ${limit + 1} OFFSET ${offset}
  `;
    const [rows] = await db_1.pool.execute(sql, [
        city.trim(),
        "Residential",
        asOf,
        months,
        asOf,
    ]);
    return {
        city: city.trim(),
        months,
        asOf,
        page,
        limit,
        hasMore: rows.length > limit,
        properties: rows.slice(0, limit),
    };
}
