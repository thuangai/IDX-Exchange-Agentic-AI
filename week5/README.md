# Week 5: Market Statistics Agent

This week adds a Python helper that answers market questions using our imported MLS data. OpenClaw runs the helper and turns the results into a readable summary.

## What it does

- Calculates average and median sold prices, price per square foot, days on market, and list-to-close price ratios.
- Compares active listing counts with sales volume.
- Shows monthly statistics and median price changes from the previous month or the same month last year.
- Supports city searches with optional ZIP code and property subtype filters.

`stats.py` produces the market summary. `trends.py` produces monthly results. Both reuse `week3/db.py` and the existing private database settings.

## Run locally

From the project root in Windows CMD, with MySQL running in Ubuntu:

```bat
.venv\Scripts\python.exe week5\stats.py Irvine
.venv\Scripts\python.exe week5\trends.py Irvine
```

Optional filters:

```bat
.venv\Scripts\python.exe week5\stats.py Irvine --zip 92618 --type Condominium
.venv\Scripts\python.exe week5\trends.py Irvine --months 12 --json
```

Both helpers accept `--as-of YYYY-MM-DD` for a fixed reporting date. Dependencies come from the root `requirements.txt`; database settings stay in the existing `.env` file.

## Use with OpenClaw

After the shared Python installation is set up, run from Windows CMD:

```bat
.venv\Scripts\python.exe install_week5.py
```

The installer copies the helpers into OpenClawGateway, tests them against MySQL, and installs the `market-statistics` skill. Start a new chat and ask:

> Use market-statistics to summarize Irvine's median sold price, days on market, list-to-close ratio, and monthly trends.

## Validation

The local helpers and installed OpenClaw skill returned matching Irvine results on October 18, 2026:

- 1,102 sold properties and 723 active listings in the snapshot.
- Median sold price: $1,494,444.
- Average days on market: 39.66.
- Average list-to-close ratio: 98%, meaning sales averaged 2% below their list prices.

## Data limits

This is an imported snapshot, not a live market feed. The inspected sales data runs from March through September 2026, with boundary months potentially incomplete. A requested 12-month window does not mean 12 complete months of data are available.

Future and invalid sale dates are excluded. Metrics omit missing or invalid inputs and report sample counts. Missing comparisons remain unavailable; there is not enough history for year-over-year results in this snapshot. Monthly price changes reflect the mix of homes sold, not appreciation of the same properties.

Keep database credentials, SQL exports, virtual environments, and Python cache files out of Git.
