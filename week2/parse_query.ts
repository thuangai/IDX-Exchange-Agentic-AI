export function parsePropertyQuery(query: string) {
  const number = (value: string) => Number(value.replace(/,/g, ""));

  const city = query.match(
    /\bin\s+([a-z]+(?:\s+[a-z]+)*?)(?=\s+(?:under|with|at|over|for|and)\b|[,.!?]|$)/i
  );

// Exclude HOA limits when looking for the home's price.
  const priceQuery = query.replace(
  /\bHOA\s+(?:under|below)\s+\$?[\d,]+(?:\.\d+)?\s*[km]?\b/gi,
  ""
  );

  const price = priceQuery.match(
  /\bunder\s+\$?([\d,]+(?:\.\d+)?)\s*([km])?\b/i
  );

  const beds = query.match(/\b(\d+)[ -]*(?:bedrooms?|beds?)\b/i);
  const baths = query.match(/\b(\d+(?:\.\d+)?)[ -]*(?:bathrooms?|baths?)\b/i);
  const sqft = query.match(/\b([\d,]+)\s*(?:sqft|sq ft|square feet)\b/i);
  const hoa = query.match(/\bHOA\s+(?:under|below)\s+\$?([\d,]+)\b/i);

  const propertyTypes: [RegExp, string][] = [
    [/\bcondos?\b|\bcondominiums?\b/i, "Condominium"],
    [/\btownhomes?\b|\btownhouses?\b/i, "Townhouse"],
    [/\bsingle[ -]family\b/i, "SingleFamilyResidence"],
    [/\bland\b/i, "UnimprovedLand"],
  ];

  const type = propertyTypes.find(([pattern]) => pattern.test(query));

  function feature(name: string): "True" | "False" | null {
    if (new RegExp(`\\b(?:no|without)\\s+(?:a\\s+)?${name}\\b`, "i").test(query)) {
      return "False";
    }
    return new RegExp(`\\b${name}\\b`, "i").test(query) ? "True" : null;
  }

  let maxPrice: number | null = null;
  if (price) {
    const suffix = price[2]?.toLowerCase();
    const multiplier = suffix === "m" ? 1_000_000 : suffix === "k" ? 1_000 : 1;
    maxPrice = number(price[1]) * multiplier;
  }

  return {
    city: city?.[1].trim() ?? null,
    maxPrice,
    beds: beds ? number(beds[1]) : null,
    baths: baths ? number(baths[1]) : null,
    sqft: sqft ? number(sqft[1]) : null,
    type: type?.[1] ?? null,
    pool: feature("pool"),
    hasView: feature("view"),
    maxHOA: hoa ? number(hoa[1]) : null,
  };
}