# Week 6: Embeddings and Vector Search

This week adds semantic property search. Instead of requiring exact keywords, it compares the meaning of a search description with listing descriptions and returns the top five matches.

## How it works

1. Read active listings with descriptions from MySQL's `rets_property` table.
2. Combine the description with city, property type, price, beds, baths, and square footage.
3. Generate Gemini embeddings and cache them in a local SQLite database.
4. Embed the search query and rank listings using cosine similarity.
5. Let OpenClaw summarize the matching homes using their actual listing remarks.

This implementation uses `gemini-embedding-001` with 3,072 dimensions, substituting Gemini for the handbook's OpenAI example. Listings use the `RETRIEVAL_DOCUMENT` task; searches use `RETRIEVAL_QUERY`.

## Setup

Run commands from the project root in Windows CMD. Keep MySQL running in Ubuntu.

```bat
.venv\Scripts\python.exe -m pip install -r week6\requirements.txt
```

Keep the existing MySQL settings and add `GEMINI_API_KEY` to your private `week3/.env` file. Never commit the key.

## Build and search

Start with a small sample:

```bat
.venv\Scripts\python.exe week6\semantic.py build --city Irvine --limit 100
```

Expand to all eligible Irvine listings:

```bat
.venv\Scripts\python.exe week6\semantic.py build --city Irvine --limit 0
```

Search the saved index:

```bat
.venv\Scripts\python.exe week6\semantic.py search "A charming home with mountain views and lots of character" --city Irvine
```

The cache is stored at `data/week6-semantic.sqlite`. Unchanged embeddings are reused, and completed batches remain saved if a build stops. Search rechecks active status and skips listings whose indexed text has changed.

## OpenClaw

Run from Windows CMD after building the index:

```bat
.venv\Scripts\python.exe install_week6.py
```

The installer copies the index and helpers into OpenClawGateway, installs dependencies, tests a search, and enables `semantic-property-search`. It does not rebuild the embeddings.

In a new OpenClaw chat, ask:

> Use semantic-property-search to find the top 5 homes in Irvine matching "a charming home with mountain views and lots of character."

## Results and limits

Tested locally and through OpenClaw with 720 indexed Irvine listings. The example returned 168 Crossover as the highest-ranked match; its description explicitly mentions mountain views.

- Coverage is limited to indexed listings, currently Irvine, within the imported snapshot. It is not live MLS availability.
- Similarity scores rank meaning; they are not probabilities or guarantees that every requested feature is present.
- City and active status are enforced. Other preferences, including budget, are not hard filters in this helper.
- Listing text is capped at 6,000 characters before embedding. Longer descriptions are truncated.
- Building and searching use Gemini API quota. Building sends listing text to the provider.

Keep `.env` files, SQL exports, the `data/` cache, `.venv/`, and `__pycache__/` out of Git. Commit source code, skill instructions, requirements, and this README.
