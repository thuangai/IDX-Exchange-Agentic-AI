import { deepStrictEqual } from "node:assert";
import { parsePropertyQuery } from "./parse_query";

const empty = {
  city: null,
  maxPrice: null,
  beds: null,
  baths: null,
  sqft: null,
  type: null,
  pool: null,
  hasView: null,
  maxHOA: null,
};

const tests: {
  query: string;
  expected: Partial<ReturnType<typeof parsePropertyQuery>>;
}[] = [
  {
    query: "Show me 3-bedroom condos in Irvine under $1.5M with a pool.",
    expected: {
      city: "Irvine", maxPrice: 1500000, beds: 3,
      type: "Condominium", pool: "True",
    },
  },
  {
    query: "Townhomes in Newport Beach under $900k",
    expected: {
      city: "Newport Beach", maxPrice: 900000, type: "Townhouse",
    },
  },
  {
    query: "Single-family homes in Pasadena with 4 beds and 2.5 baths",
    expected: {
      city: "Pasadena", beds: 4, baths: 2.5,
      type: "SingleFamilyResidence",
    },
  },
  {
    query: "Land in Riverside under $250,000",
    expected: {
      city: "Riverside", maxPrice: 250000, type: "UnimprovedLand",
    },
  },
  {
    query: "Homes with 1,800 square feet",
    expected: { sqft: 1800 },
  },
  {
    query: "Condos with HOA under $500",
    expected: { type: "Condominium", maxHOA: 500 },
  },
  {
    query: "Homes without a pool",
    expected: { pool: "False" },
  },
  {
    query: "Homes with a view",
    expected: { hasView: "True" },
  },
  {
    query: "Homes with no view and 2 bedrooms",
    expected: { hasView: "False", beds: 2 },
  },
  {
    query: "Show me homes",
    expected: {},
  },
];

let failed = 0;

for (const [index, test] of tests.entries()) {
  try {
    deepStrictEqual(
      parsePropertyQuery(test.query),
      { ...empty, ...test.expected }
    );
    console.log(`PASS ${index + 1}: ${test.query}`);
  } catch (error) {
    failed++;
    console.error(`FAIL ${index + 1}: ${test.query}`);
    console.error(error);
  }
}

console.log(`\n${tests.length - failed}/${tests.length} passed`);
process.exitCode = failed ? 1 : 0;