# California Whitewater

A curated database and (eventually) app for California whitewater kayaking runs, with an emphasis on honest handling of rating disputes and source provenance.

## Why this exists

Existing lists of California whitewater runs — riverfacts.com, guidebook indexes, outfitter rosters — each have problems:

- **riverfacts.com** is comprehensive (~267 runs) but mostly mirrors Holbek & Stanley's 1988–1998 ratings, which have drifted with boat technology, wood accumulation, and community consensus.
- **Guidebooks** are curated but dated, and the two main California guidebooks (Holbek & Stanley, Cassady & Calhoun) sometimes rate the same run differently.
- **Commercial outfitters** inflate ratings for liability and marketing. A "Class V" commercial trip may be a kayaker's IV+.
- **Expert kayaker blogs** (McQuoid, awetstate, liquidlore) are accurate but scattered.

The key insight: a run doesn't have one rating. It has many ratings across sources, flow levels, and time periods. This project stores them all.

## What's here now

- `CLAUDE.md` — project instructions for Claude Code
- `docs/` — three curated analyses of California Class III, IV, and V runs
- `reference/` — methodology, source trust hierarchy, rating disputes, corrections log, glossary, schema notes
- `data/` — (empty) where the database will live
- `app/` — (empty) where the application code will live

## What's next

Open questions the project needs to answer in order:

1. **Database choice** — SQLite vs Postgres. Recommend: SQLite to start.
2. **Language/stack** — Rust (sqlx, axum) vs Python (FastAPI, SQLAlchemy) vs TypeScript (Drizzle, Hono). Stack-agnostic schema proposed in `reference/schema-notes.md`.
3. **Seeding approach** — parse the curated docs into database rows, or ingest-from-scratch with source attribution. Recommend: parse the docs, then use that as the baseline for source-attributed rows.
4. **App shape** — query/filter UI? Progression planner? Flow dashboard? Paper-map–style visualizer?
5. **Deployment** — local-only, or web app for personal use?

## Working with Claude Code on this project

Open Claude Code in this directory. It will automatically load `CLAUDE.md` which contains:

- Project context and owner preferences
- Source trust hierarchy
- Rating-dispute handling rules
- Schema invariants (most importantly: ratings as data, not attributes)
- Anti-patterns to avoid
- Pointers to the detailed reference docs

For any non-trivial task, Claude will also want to consult:

- `reference/methodology.md` for how the curation was done
- `reference/schema-notes.md` for database design
- `reference/rating-disputes.md` for the edge cases

## Curated docs are the baseline truth

The three files in `docs/` represent careful curation. Treat them as the baseline content for the database. Corrections happen via `reference/corrections-log.md` with source and date.

## A note on scope

This is a personal project, not a commercial product. It scratches the itch of wanting a database that treats California whitewater with the rigor the subject deserves. If it becomes useful to others, that's a bonus.
