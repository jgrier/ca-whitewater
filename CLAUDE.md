# California Whitewater Project

Database and app for California whitewater runs, rated by difficulty class, with an emphasis on honest handling of rating disputes and source reliability.

## Project owner context

- **Paddler**: Jamie, based in Rocklin, CA. Intermediate-to-advanced kayaker. Has paddled East Fork Carson overnight and South Fork American (C-to-G). Values multi-day wilderness trips. Lone-wolf preference — this is a personal project, not a commercial venture.
- **Location matters**: Rocklin is the gateway to the best CA Class III/IV region in the state (NF American, MF American, Upper Sac, Pit, NF Feather, NF Yuba, Mokelumne, Goodwin). Proximity-aware features are valuable.
- **Technical background**: Senior SWE. Comfortable with databases, TypeScript, Python, Rust. Uses Claude Code as primary interface.

## What this project is (and isn't)

**Is**: A curated, source-rigorous database of CA whitewater runs that surfaces rating disputes and flow-dependent behavior honestly, plus an app layer for querying/planning.

**Is not**: Another scraper of riverfacts.com. The whole point is that single-source lists are misleading — especially for Class IV/V runs where kayaker consensus diverges from raft-outfitter ratings.

## Core design invariant: ratings as data, not attributes

**This is the single most important rule.** Do not add a single `class` or `rating` column to the `runs` table. A run has multiple ratings depending on source, flow, era, and paddler perspective. Store them all.

```
runs (one row per run)           — name, drainage, put-in, take-out, mileage, gradient
ratings (many rows per run)      — one per source × flow-context × as-of-date
sources                          — with trust weights for sport vs expert runs
flow_windows                     — season, dam-controlled, gauge_id, cfs ranges
hazards                          — wood, sieves, mandatory portages, with dates
```

See `@reference/schema-notes.md` for the full rationale and the rating-dispute cases that drove this design.

## Source trust hierarchy

Not all sources are equal. Use these weights when ingesting or surfacing ratings:

**For expert (V / IV+) runs** — trust kayaker-perspective sources:
1. Darin McQuoid (`darinmcquoid.com`) — highest authority for CA expert V/V+
2. American Whitewater river pages
3. Whitewater Guidebook (Zach Collier)
4. awetstate.com, liquidlore.com, Oregon Kayaking — trip-report perspective
5. cacreeks.com (Bill Tuthill) — neutral, kayaker-focused
6. Commercial outfitters — **distrust at V level**, they inflate ratings conservatively
7. riverfacts.com / Holbek-Stanley — foundational but often dated (1988–98)

**For sport (III / easy IV) runs** — commercial outfitters are reasonable:
1. American Whitewater
2. Whitewater Guidebook
3. Commercial outfitters (OARS, Momentum, Whitewater Voyages, local operators)
4. cacreeks.com
5. riverfacts.com

See `@reference/sources.md` for full URLs, coverage notes, and known biases.

## Rating dispute handling

Some runs have legitimate community disagreement. Never collapse these to a single rating.

Key disputed runs to be aware of:
- **NF Feather Tobin**: McQuoid V / awetstate IV with V-consequence sieves / Holbek-Stanley III-V
- **MF Feather Bald Rock**: AW/WG V+ / liquidlore IV+/V / McQuoid "V (P)"
- **Lower Kern Miracle→Democrat**: rafters call it IV, has V+ mandatory portage at Royal Flush
- **Merced El Portal**: III+ at low / IV+ at high / contains V Ned's Gulch
- **Cal Salmon Nordheimer**: marketed as "IV step-up," has 3 mandatory Vs → it's a V run

See `@reference/rating-disputes.md` for the full list with reasoning.

## Anti-patterns — don't do these

- **Don't rate a run as III just because riverfacts says "III-IV"**. Check what the V rapids in that run are and whether kayakers treat them as portageable or mandatory.
- **Don't conflate "commercial IV" with "kayaker IV"**. Commercial outfitters mean "guided with safety boats." Kayakers mean "self-rescue in this water."
- **Don't assume outdated ratings are current**. Many Holbek/Stanley ratings are from 1988–98. Wood and channel changes matter at IV/V.
- **Don't auto-classify a run by the max-rated rapid**. A Class III run with one portaged V+ is still a III for the purpose of "what can a III paddler do." Store both.
- **Don't scrape without attribution**. Track which source each rating came from in the database.

## Working docs structure

- `@docs/class-III.md`, `@docs/class-IV.md`, `@docs/class-V.md` — the existing curated analyses. Treat these as authoritative baseline content; the database should be seeded from them.
- `@reference/methodology.md` — the three-pass method used to produce the docs
- `@reference/sources.md` — source trust hierarchy and URLs
- `@reference/rating-disputes.md` — the disputed-rating cases
- `@reference/corrections-log.md` — errors found and fixed during the curation work
- `@reference/glossary.md` — terminology
- `@reference/schema-notes.md` — database design rationale
- `data/` — the actual database, seeds, migrations (currently empty)
- `app/` — application code (currently empty)

## Conventions

- **Markdown docs**: kebab-case filenames. Class docs capitalize the Roman numeral (`class-III.md`).
- **Dates in data**: ISO 8601 (`2026-04-19`). Ratings have `as_of_date` so temporal drift is visible.
- **Flow units**: CFS (cubic feet per second). Always. Never convert silently.
- **Difficulty strings**: preserve the source's original format (`"III+"`, `"IV-V"`, `"IV(V)"`, `"III-V(V+)"`). Don't normalize away the qualifiers — they carry information.
- **Run names**: use the kayaker-common name (e.g., "Chamberlain Falls," "Goodwin Canyon," "Banzai") not the database path. Store both.

## When to consult what

- Starting anything new → read this file (which you're doing) and `@reference/methodology.md`
- Working on schema → `@reference/schema-notes.md` and `@reference/rating-disputes.md`
- Seeding the database from the curated docs → `@docs/class-III.md`, `@docs/class-IV.md`, `@docs/class-V.md`
- Evaluating a new source or rating → `@reference/sources.md`
- User asks "why is run X rated Y?" → `@reference/rating-disputes.md` first, then the class doc

## What not to re-derive

The three class docs represent real work. If they appear wrong, treat that as a data-quality issue to investigate, not a reason to re-curate from scratch. Corrections go in `@reference/corrections-log.md` with source and date.
