# Methodology

How the class-III/IV/V documents were produced. This is the reasoning you'd need to reproduce or extend the work.

## The three-pass approach

### Pass 1 — Database enumeration

Start with the riverfacts.com California list (~267 runs), which mirrors the Holbek & Stanley catalog plus some later additions. This is the broadest inventory of named CA runs with ratings.

Filter by class character:
- **Class III**: any rating containing III (`III`, `III+`, `II-III`, `III-IV`, `II-IV`, `III-V`)
- **Class IV**: any rating with IV as modal character
- **Class V**: any rating with V as modal character, plus portage-gated runs marked `(V)` / `(V+)`

Exclusions:
- Pure II runs
- Runs where the higher class is incidental (e.g., a mostly-II run with one portaged V+)

This produces a candidate set. It is **not** a classics list — riverfacts ratings are often dated (1988–98 Holbek/Stanley origin) and don't reflect kayaker consensus.

### Pass 2 — Editorial curation

Cross-reference the candidate set against authorities who curate rather than enumerate:

- **Whitewater Guidebook** (whitewaterguidebook.com) — editorially selective, good breakdowns
- **American Whitewater** river detail pages — community-maintained
- **Darin McQuoid's site** (darinmcquoid.com) — authoritative for expert V/V+
- **cacreeks.com** (Bill Tuthill) — neutral, accurate mileage/gradient/flow data
- **awetstate.com, liquidlore.com, Oregon Kayaking** — kayaker trip reports
- **Commercial outfitter rosters** — signals that a run is run-able commercially; de facto classic for III/IV sport runs

If a run is in the enumeration but not editorially curated anywhere, it's probably obscure, overly hazardous, or access-restricted — demote or exclude.

### Pass 3 — Community signal proxy

A run is a **classic** if it shows up in "best of" lists, club write-ups, Mountain Buzz discussion, race events, or paddler bucket-list articles. This corrects for editorial bias (a guidebook author may love a run that nobody actually paddles).

Proxy signals:
- Commercial outfitters market it regularly → classic III/IV
- Featured in Adventure Sports Journal, American Whitewater Journal → classic IV/V
- Has a named race (Cherry Creek Race, Moke Races) → classic
- Multiple kayaker blog write-ups → classic
- Only named as a "first descent" or by Scott Lindgren / Darin McQuoid / Rush Sturges → expedition V, elite

## Tier construction

A run earns "classic" if it scores across at least two of the three passes AND is predominantly the target class at normal kayaking flows.

- **Tier 1** — iconic, must-do, multi-source unanimous
- **Tier 2** — well-established regional classic
- **Tier 3** — local / rarely-run / rain-dependent / expedition

## Known methodology weaknesses

### Commercial outfitter bias for III/IV
Commercial offerings over-represent dam-released summer rivers. Rain-dependent and snowmelt-short-window runs are under-represented in outfitter rosters even when they're loved by locals.

### Kayaker-blogger bias for V
Expert V coverage is heavily weighted toward the NorCal / Sierra creeks where the blogger community lives. SoCal and coastal-range V is probably under-covered.

### Sacramento/Bay-Area-paddler bias overall
The mental model of "classics" reflects where most CA paddlers live. A Humboldt County or Kern County paddler would produce a meaningfully different list.

### Temporal drift
Many underlying ratings are from Holbek & Stanley's 1988/1998 editions. Wood, channel change, and paddler skill evolution mean the paper ratings may lag reality. At IV/V this gap matters.

### Rating diversity within a single run
"Tuolumne Main" at 1000 cfs vs 4500 cfs is two different runs. Single rating labels hide this. The database schema (see `schema-notes.md`) addresses this with `flow_windows` and flow-tagged ratings.

### No trip-report count data
I did not pull American Whitewater's trip-report counts directly (AW needs JavaScript; its API is not documented well). Community signal proxy is my stand-in. A future data-pull from AW would improve the popularity rankings.

## Reproducing for other states / regions

The method generalizes. For any region:
1. Find the equivalent of riverfacts.com — a comprehensive regional database
2. Identify 3–5 authoritative kayaker sources with trip-report-quality content
3. Identify the commercial-outfitter set (signal for sport-class classics)
4. Identify the community signal proxy (blogs, forums, races)
5. Run the three passes, build tiers

For states with less density (Oregon, Washington), you may need to lean harder on pass 2 (editorial curation) because the enumerated database will include fewer runs.

## What I didn't do

- Did not pull AW trip-report counts
- Did not verify current wood/hazard status for any specific run
- Did not verify permit/access status
- Did not cross-reference Cassady & Calhoun systematically (only excerpts on tuolumne-river.com and merced-river.com)
- Did not normalize ratings across sources into a single scale
- Did not filter by proximity to any particular location

Each of these is a reasonable next step.
