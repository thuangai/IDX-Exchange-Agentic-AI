# Week 2: Property Query Parser

This project converts a property-search sentence into JSON filters using TypeScript. An OpenClaw skill runs the parser and returns its output.

It extracts city, price limit, bedrooms, bathrooms, square footage, property type, pool, view, and HOA limit. Missing fields return `null`.

## Example

Input:
> Condos in Irvine under $900k with a pool

Output:
```json
{
  "city": "Irvine",
  "maxPrice": 900000,
  "beds": null,
  "baths": null,
  "sqft": null,
  "type": "Condominium",
  "pool": "True",
  "hasView": null,
  "maxHOA": null
}
```

## Run locally

Requires Node.js. Run these commands in PowerShell from the `week2` folder:

```powershell
npm.cmd ci
npx.cmd tsx cli.ts 'Condos in Irvine under $900k with a pool'
```

## Tests

```powershell
npx.cmd tsx test_queries.ts
```

All 10 test queries passed, covering prices, property types, bedrooms, bathrooms, square footage, HOA limits, pool/view preferences, and unspecified fields.

## Build

```powershell
npx.cmd tsc parse_query.ts cli.ts --outDir dist --module commonjs --target ES2022 --types node --skipLibCheck
node .\dist\cli.js 'Condos in Irvine under $900k with a pool'
```

## OpenClaw integration

The installed skill folder is:
`~/.openclaw/workspace/skills/property-query/`

Copy `SKILL.md` into that folder and the compiled `dist/cli.js` and `dist/parse_query.js` into its `scripts/` subfolder.

In a new OpenClaw chat, ask:
> Use the property-query skill to parse: Condos in Irvine under $900k with a pool.

The skill was tested in OpenClaw and returned structured filters after executing the script.

## Limitations

The parser uses regular expressions and supports a limited set of phrases. It may miss unfamiliar wording. This week only produces filters; it does not query MySQL or return property listings.