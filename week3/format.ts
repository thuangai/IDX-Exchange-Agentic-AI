type Property = Record<string, unknown>;

function numberText(value: unknown, currency = false): string {
  if (value === null || value === undefined || value === "") {
    return "Unknown";
  }

  const number = Number(value);
  if (!Number.isFinite(number)) return "Unknown";

  return currency
    ? number.toLocaleString("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
      })
    : number.toLocaleString("en-US");
}

export function formatCards(
  properties: Property[],
  mode: "active" | "sold"
): string {
  if (properties.length === 0) {
    return "No matching properties found.";
  }

  return properties.map((property, index) => {
    const lines = [
      `${index + 1}. ${property.address || "Address unavailable"}, ${property.city || "City unavailable"}`,
      `${mode === "sold" ? "Sold price" : "List price"}: ${numberText(property.price, true)}`,
      `Beds: ${numberText(property.beds)} | Baths: ${numberText(property.baths)} | Sqft: ${numberText(property.sqft)}`,
      `Type: ${property.type || "Unknown"}`,
      `Listing ID: ${property.listingId ?? "Unknown"}`,
    ];

    if (mode === "sold") {
      lines.push(`Closed: ${property.closeDate ?? "Unknown"}`);
    } else {
      lines.push(`HOA fee: ${numberText(property.hoa, true)}`);
      lines.push(`Photos: ${numberText(property.photoCount)}`);
    }

    return lines.join("\n");
  }).join("\n\n");
}