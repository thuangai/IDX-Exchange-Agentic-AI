# Week 4: Conversational Property Search

The `property-chat` OpenClaw skill turns the Week 3 database search into a conversation. It asks for missing preferences, remembers earlier answers, and searches again when preferences change.

## Features

- Follow-up questions for city, budget, and property type.
- Saved filters across separate helper calls.
- Separate state files for each conversation/session ID.
- Budget and preference refinement.
- “Any type” to skip the property-type filter.
- “Start over” to clear saved preferences.
- Property cards with address, price, beds, baths, and photo count.

## Example conversation

1. “Find homes in Irvine”
2. “Under $1.2M”
3. “Single family with at least 3 beds”
4. “Under $1.5M”

The last message changes the budget while retaining Irvine, single-family, and at least 3 bedrooms.

## Run locally

Requires the Week 2 parser and Week 3 dependencies/database settings.
Keep Ubuntu running with MySQL started.

From `week3` in Windows Command Prompt:

```cmd
node_modules\.bin\tsx.cmd ..\week4\cli.ts demo "Start over"
node_modules\.bin\tsx.cmd ..\week4\cli.ts demo "Find homes in Irvine"
node_modules\.bin\tsx.cmd ..\week4\cli.ts demo "Under $1.2M"
node_modules\.bin\tsx.cmd ..\week4\cli.ts demo "Single family with at least 3 beds"
node_modules\.bin\tsx.cmd ..\week4\cli.ts demo "Under $1.5M"
```

`demo` is a local test session ID. OpenClaw must use a trusted, stable
conversation identifier and keep different conversations separate.

## Build

From `week3`:

```cmd
node_modules\.bin\tsc.cmd ..\week4\cli.ts --outDir ..\week4\dist --rootDir .. --module commonjs --target ES2022 --types node --skipLibCheck
```

## OpenClaw setup

Install `SKILL.md`, the compiled `dist` folder, and Week 3 package files
under `~/.openclaw/workspace/skills/property-chat/`.

Add a private database `.env` in that skill folder and install runtime
dependencies with `npm ci --omit=dev --ignore-scripts`.

The Node path in `SKILL.md` is specific to my installation.

## Session storage

State is stored outside the repository in:
`~/.idx-exchange/week4-sessions/`

Each session ID maps to a hashed filename. Calls within a conversation
must run sequentially. Saved state remains until reset; this prototype
does not expire sessions automatically.

## Validation

- Preferences persisted across separate process runs.
- Follow-up questions collected city, budget, and property type.
- Budget refinement preserved the other filters.
- Database cards included photo counts.
- The conversation and refinement were tested through WhatsApp.

## Limitations

The parser supports limited wording. Results come from an imported
MLS dataset, not a live feed. The agent sometimes used confusing
“loop” wording, although the tested conversation continued and
returned matching results.