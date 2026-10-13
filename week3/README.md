# Week 3: MLS Database Integration

This project connects the Week 2 property-query parser to MySQL.
The OpenClaw `mls-search` skill runs the code and returns property cards.

## Features

- Active listing searches in `rets_property`.
- Residential sold-property searches in `california_sold`.
- Prepared statements for filter values.
- Validated pagination, with up to 50 properties per page.
- Readable cards and a message when no properties match.
- Recent-sales searches exclude future dates.

## Setup

Requires Node.js and the imported `idx_exchange` MySQL database.
Run from the `week3` folder in PowerShell:

```powershell
npm.cmd ci
```

Create a private `.env` file:

```dotenv
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=idx_user
MYSQL_PASSWORD="your_local_mysql_password"
MYSQL_DATABASE=idx_exchange
```

Use a database account with SELECT access.
In this Windows/WSL setup, keep Ubuntu running with MySQL started.

## Run

```powershell
npx.cmd tsx test_db.ts
npx.cmd tsx cli.ts active 'Condos in Irvine under $900k' 1 5
npx.cmd tsx cli.ts active 'Condos in Irvine under $900k' 2 5
npx.cmd tsx cli.ts sold Irvine 1 5 12
```

Active arguments: query, page, limit.
Sold arguments: city, page, limit, months.

## Build and OpenClaw

```powershell
npx.cmd tsc cli.ts --outDir dist --rootDir .. --module commonjs --target ES2022 --types node --skipLibCheck
```

The build includes the Week 2 parser and preserves its relative import.

The installed skill lives at:
`~/.openclaw/workspace/skills/mls-search/`

It contains `SKILL.md`, the `dist` folder, package files, and a private
`.env`. Install runtime dependencies in that folder with:
`npm ci --omit=dev --ignore-scripts`

The Node path in `SKILL.md` is specific to my OpenClaw installation
and should be adjusted on another machine.

Example chat request:
> Use mls-search to find condos in Irvine under $900k. Show page 1 with 5 cards.

## Checks completed

- Database connection and row counts.
- Active searches and distinct pages 1 and 2.
- Recent sold-property searches.
- No-match handling.
- Active searches, pagination, sold searches, and no matches through OpenClaw.

## Limitations

Results come from an imported dataset, not a live MLS feed.
The Week 2 parser supports limited wording.
Blank pool/view values are treated as unknown.
Sold comparisons use city and date only; they are not valuations.