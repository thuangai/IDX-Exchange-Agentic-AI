"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.searchActiveListings = searchActiveListings;
const db_1 = require("./db");
async function searchActiveListings(filters, page = 1, limit = 5) {
    if (!Number.isSafeInteger(page) || page < 1) {
        throw new Error("Page must be a positive integer.");
    }
    if (!Number.isSafeInteger(limit) || limit < 1 || limit > 50) {
        throw new Error("Limit must be between 1 and 50.");
    }
    const offset = (page - 1) * limit;
    if (!Number.isSafeInteger(offset)) {
        throw new Error("Page is too large.");
    }
    const conditions = ["L_Status = ?"];
    const params = ["Active"];
    function add(condition, value) {
        conditions.push(condition);
        params.push(value);
    }
    if (filters.city !== null) {
        add("L_City = ?", filters.city);
    }
    if (filters.type !== null) {
        add("L_Type_ = ?", filters.type);
    }
    const numericFilters = [
        ["maxPrice", "L_SystemPrice <= ?"],
        ["beds", "L_Keyword2 >= ?"],
        ["baths", "LM_Dec_3 >= ?"],
        ["sqft", "LM_Int2_3 >= ?"],
        ["maxHOA", "AssociationFee <= ?"],
    ];
    for (const [key, condition] of numericFilters) {
        const value = filters[key];
        if (value !== null) {
            if (!Number.isFinite(value) || value < 0) {
                throw new Error(`Invalid value for ${key}.`);
            }
            add(condition, value);
        }
    }
    // Match explicit true/false values; leave blank and NULL unknown.
    for (const [value, column] of [
        [filters.pool, "PoolPrivateYN"],
        [filters.hasView, "ViewYN"],
    ]) {
        if (value !== null) {
            add(`LOWER(TRIM(${column})) IN (?, ?)`, value === "True" ? "1" : "0");
            params.push(value.toLowerCase());
        }
    }
    // Pagination numbers are validated integers above.
    // All property filter values use prepared-statement placeholders.
    const sql = `
    SELECT
      id, L_ListingID AS listingId,
      L_Address AS address, L_City AS city, L_Zip AS zip,
      L_SystemPrice AS price, L_Keyword2 AS beds,
      LM_Dec_3 AS baths, LM_Int2_3 AS sqft,
      L_Type_ AS type, L_Status AS status,
      AssociationFee AS hoa,
      PoolPrivateYN AS pool, ViewYN AS hasView
    FROM rets_property
    WHERE ${conditions.join(" AND ")}
    ORDER BY L_SystemPrice ASC, id ASC
    LIMIT ${limit + 1} OFFSET ${offset}
  `;
    const [rows] = await db_1.pool.execute(sql, params);
    return {
        page,
        limit,
        hasMore: rows.length > limit,
        properties: rows.slice(0, limit),
    };
}
