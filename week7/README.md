# Week 7: Recommendation Engine

This week builds on Week 6's semantic search. Given a listing the user likes, the helper recommends five similar active homes and compares their asking prices with recent sold properties.

## Recommendation scoring

Each candidate gets up to 60 structured points:

| Feature | Points |
| --- | --- |
| Price difference under $50,000 / $150,000 / $300,000 | 20 / 12 / 5 |
| Same bedroom count | 15 |
| Same city | 15 |
| Square footage difference under 300 / 700 | 10 / 5 |

The semantic component adds 40 times the cosine similarity between the two cached Gemini embeddings. The reference listing is excluded, and candidates must still be active with unchanged indexed text. Scores rank similarity; they are not probabilities.

Property type and bathroom count are displayed but are not structured scoring components in the handbook model. Recommendations can therefore include different property types.

## Sold-price comparisons

For each recommended home, query `california_sold` for residential sales in the same city and, when known, the same property subtype. Use the prior six calendar months and square footage within +/-20% of the candidate. Exclude future dates and invalid prices or areas.

The baseline equals average sold price per square foot multiplied by the candidate's square footage. The output includes the comparable count, observed sale-date range, baseline, and percentage difference from asking price. Positive means asking above the baseline; negative means below. Fewer than five comparables is flagged as a limited sample; no matching comparables produces an unavailable assessment.

## Run locally

Use Windows CMD from the project root, with MySQL running in Ubuntu and the Week 6 index already built:

```bat
.venv\Scripts\python.exe week7\recommend.py 1182905312
```

For a reproducible reporting date:

```bat
.venv\Scripts\python.exe week7\recommend.py 1182905312 --as-of 2026-11-01
```

The helper reuses `week3/db.py`, `week6/semantic.py`, and `data/week6-semantic.sqlite`. No additional packages or embedding API requests are needed for recommendation scoring.

## OpenClaw

After the Week 6 OpenClaw installation, run from Windows CMD:

```bat
.venv\Scripts\python.exe install_week7.py
```

Start a new OpenClaw chat and ask:

> Use property-recommendations to recommend five homes similar to listing 1182905312. Include similarity scores and sold-comparable price comparisons.

## Validation and limitations

The reference home, 168 Crossover, was excluded from 720 indexed Irvine listings, leaving 719 candidates. The top recommendation was 6 Recodo, scoring 96.08 points. Its $2,649,900 asking price was 8.8% below a $2,905,642.17 baseline from 125 sold comparables. The installed helper returned matching results, and the visible OpenClaw response matched those values.

Results cover the local index within an imported MLS snapshot, not live availability. The initial index covers Irvine. A requested six-month sales window does not guarantee complete coverage: the inspected comparables ended in September 2026. The baseline is a simple comparison, not an appraisal or proof that a home is fairly priced. It does not adjust for condition, neighborhood, renovations, or all property differences.

Keep `.env` files, SQL exports, the embedding cache, virtual environments, and Python cache files out of Git.
