---
name: property-recommendations
description: Recommend the top five active properties similar to a listing the user likes, combining structured and embedding scores with recent sold-comparable price assessments. Use when given a reference listing ID and asked for similar homes or alternatives.
---

Ask for the reference listing ID if it is not provided. Run this helper once, safely quoting the ID:

```bash
"{baseDir}/../../idx-exchange-python/.venv/bin/python" "{baseDir}/../../idx-exchange-python/week7/recommend.py" '1182905312'
```

Replace the example ID with the user's listing ID. Use --as-of YYYY-MM-DD only when requested.
Use the actual helper output, not remembered results. The helper reuses cached Gemini vectors and makes no embedding API requests.
Summarize the reference property and state indexed_candidates_scored. Present up to five returned recommendations,
ordered exactly as returned, using bullets or correctly numbered items 1 through 5.
For each include address, listing ID, type, asking price, beds, baths, square footage,
total score, and a short explanation from structured_breakdown and cosine_similarity.
The score is up to 60 structured points plus 40 times cosine similarity, not a probability.
Property type and bathrooms are displayed but not components of the handbook's structured score;
do not claim every recommendation has the same type or bathroom count as the reference.

Include each recommendation's comp_count, comp_based_price, difference_pct, and observed comparable date range.
Positive difference_pct means asking above the baseline; negative means below. Explain this clearly.
If assessment is limited_sample, mention the small sample. If unavailable, say why and do not invent a value.
The baseline uses average sold price per square foot times the candidate's area, matching city and known subtype,
within +/-20% area and the prior six calendar months, excluding future dates.
Call it a sold-comparable baseline, never an appraisal, fair-value guarantee, or proof a home is underpriced.
Do not claim all six months have complete records. Report the actual first and last comparable dates.
State that results cover fresh indexed active listings within an imported snapshot, not live MLS availability.
The initial index covers Irvine. Never silently expand an index or generate embeddings.
If execution fails, briefly report the error; do not loop, invent listings, or print private settings.
