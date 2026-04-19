# Schema Notes

Database design rationale for the CA whitewater project. The schema exists to support the core invariant: **ratings are data, not attributes.** Every run has multiple ratings from multiple sources across multiple flow contexts and time periods, and all of them matter.

## The design tension

The obvious schema is wrong:

```sql
-- DO NOT DO THIS
CREATE TABLE runs (
    id INT PRIMARY KEY,
    name TEXT,
    class TEXT,  -- "IV+" <-- which source's IV+? at what flow? as of when?
    ...
);
```

This collapses all the hard-won information. Tobin becomes "IV or V, pick one." Merced El Portal becomes "III or IV or V depending on flow, lose the nuance." Any rating dispute gets resolved by whichever source you happened to scrape last.

The correct schema treats ratings as first-class entities with provenance.

## Proposed schema (v0)

```sql
-- Core run identity
CREATE TABLE runs (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,            -- "Chamberlain Falls"
    alt_names        TEXT[],                   -- ["Mineral Bar to Yankee Jim's"]
    drainage         TEXT NOT NULL,            -- "American River"
    fork             TEXT,                     -- "North Fork"
    region           TEXT NOT NULL,            -- "Sierra", "Klamath", "Coast Range"
    state            TEXT DEFAULT 'CA',
    county           TEXT,
    put_in_name      TEXT,                     -- "Mineral Bar Campground"
    put_in_lat       DECIMAL(9,6),
    put_in_lng       DECIMAL(9,6),
    take_out_name    TEXT,
    take_out_lat     DECIMAL(9,6),
    take_out_lng     DECIMAL(9,6),
    mileage          DECIMAL(5,2),
    gradient_fpm     INTEGER,                  -- feet per mile
    notes            TEXT,
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Sources of ratings and information
CREATE TABLE sources (
    id                      INTEGER PRIMARY KEY,
    short_code              TEXT UNIQUE NOT NULL,  -- "mcquoid", "aw", "wg"
    name                    TEXT NOT NULL,
    url                     TEXT,
    source_type             TEXT NOT NULL,         -- "book", "website", "outfitter", "paddler_blog"
    trust_weight_sport      DECIMAL(3,2),          -- 0.00 to 1.00
    trust_weight_expert     DECIMAL(3,2),
    notes                   TEXT
);

-- Ratings: the heart of the schema. Many per run.
CREATE TABLE ratings (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    source_id           INTEGER NOT NULL REFERENCES sources(id),
    rating_raw          TEXT NOT NULL,        -- "IV+", "III-V(V+)", "V (P)" — preserve source format
    rating_low          TEXT,                 -- "III"
    rating_high         TEXT,                 -- "V"
    rating_modal        TEXT,                 -- "IV" — the typical experience
    portage_rating      TEXT,                 -- "V+" if there's a portage-gated drop
    has_mandatory_portage BOOLEAN DEFAULT FALSE,
    flow_context        TEXT,                 -- "low", "normal", "high", or specific like "@1500cfs"
    cfs_min             INTEGER,              -- if flow-specific
    cfs_max             INTEGER,
    as_of_date          DATE NOT NULL,        -- when source published this rating
    source_url          TEXT,                 -- specific page
    notes               TEXT,
    UNIQUE (run_id, source_id, flow_context, as_of_date)
);

-- Flow windows: when a run is runnable
CREATE TABLE flow_windows (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    season_start_month  INTEGER CHECK (season_start_month BETWEEN 1 AND 12),
    season_end_month    INTEGER CHECK (season_end_month BETWEEN 1 AND 12),
    dam_controlled      BOOLEAN DEFAULT FALSE,
    gauge_name          TEXT,                 -- "NF American at North Fork Dam"
    gauge_url           TEXT,                 -- Dreamflows or USGS URL
    cfs_min_runnable    INTEGER,
    cfs_max_runnable    INTEGER,
    cfs_ideal_low       INTEGER,
    cfs_ideal_high      INTEGER,
    notes               TEXT                  -- "Scheduled releases first weekend May"
);

-- Hazards: time-dependent beta
CREATE TABLE hazards (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    hazard_type         TEXT NOT NULL,        -- "wood", "sieve", "entrapment",
                                              -- "mandatory_portage", "sieve_prone",
                                              -- "undercut", "access_issue"
    location_description TEXT,                -- "Second rapid below put-in"
    rapid_name          TEXT,                 -- if hazard is at a specific named rapid
    severity            TEXT,                 -- "advisory", "serious", "fatal_if_swum"
    description         TEXT,
    reported_by         TEXT,                 -- source attribution
    as_of_date          DATE NOT NULL,
    still_present       BOOLEAN DEFAULT TRUE,
    notes               TEXT
);

-- Named rapids within runs
CREATE TABLE rapids (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    name                TEXT NOT NULL,        -- "Chamberlain Falls"
    mile                DECIMAL(4,2),         -- miles from put-in
    rating              TEXT,                 -- "IV+"
    must_scout          BOOLEAN DEFAULT FALSE,
    must_portage        BOOLEAN DEFAULT FALSE,
    description         TEXT
);

-- Classifications for filtering/display (derived, not authoritative)
CREATE TABLE run_classifications (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    classification      TEXT NOT NULL,        -- "tier_1_iii", "tier_2_iv", "expedition_v"
    rationale           TEXT,
    assigned_at         DATE NOT NULL
);

-- Overnight / multi-day capability
CREATE TABLE trip_formats (
    id                  INTEGER PRIMARY KEY,
    run_id              INTEGER NOT NULL REFERENCES runs(id),
    format              TEXT,                 -- "day", "overnight", "expedition"
    typical_days        INTEGER,
    camping_available   BOOLEAN,
    permit_required     BOOLEAN,
    permit_info         TEXT
);
```

## Key design decisions

### 1. Preserve raw rating strings

`ratings.rating_raw` stores the source's exact format ("III-V(V+)"). Parse into `rating_low`/`rating_high`/`portage_rating` separately for query efficiency, but never lose the original. If a source updates, store both and keep the older as history.

### 2. Sources table with separate sport/expert trust weights

McQuoid is the highest authority for V/V+ runs but might not even cover III runs. OARS is useful for III/IV but distorts V. Two separate trust columns capture this without needing complex logic.

Initial trust weights (seed data):

| Source | sport | expert |
|---|---|---|
| mcquoid | 0.80 | 1.00 |
| aw | 0.90 | 0.90 |
| wg | 0.90 | 0.85 |
| cacreeks | 0.85 | 0.85 |
| awetstate | 0.80 | 0.85 |
| liquidlore | 0.70 | 0.85 |
| holbek_stanley | 0.80 | 0.70 |
| cassady_calhoun | 0.90 | 0.70 |
| riverfacts | 0.65 | 0.55 |
| outfitter_momentum | 0.85 | 0.60 |
| outfitter_oars | 0.85 | 0.55 |
| outfitter_sierra_mac | 0.80 | 0.70 |

These are editable. The key invariant is that expert ratings trust McQuoid > AW > WG > everyone else, while sport ratings trust outfitters and AW roughly equally.

### 3. Flow context as a dimension on ratings

Tuolumne Main at 1000 cfs (IV+) and at 4500 cfs (V) are two ratings for the same source. `flow_context` + `cfs_min`/`cfs_max` captures this. A single run can have many ratings from a single source if that source rates it differently at different flows.

### 4. Hazards table is time-aware

Wood and channel change year-over-year. `as_of_date` + `still_present` lets the app surface current beta vs historical. When a source reports a new hazard, add a row; don't overwrite.

### 5. Rapids are entities

Named rapids (Troublemaker, Chamberlain Falls, Clavey Falls, Royal Flush) are queryable entities with their own ratings and portage flags. This lets the app answer "what's the hardest rapid on this run?" or "what's the Class V rapid I need to portage on the Lower Kern?" without parsing free text.

### 6. Classifications are derived, not authoritative

`run_classifications` (tier 1 III, tier 2 IV, expedition V, etc.) is useful for display and filtering, but these are opinions. Store them with a rationale and an assigned_at date. If you want to re-classify, add a new row.

### 7. Mileage and gradient live on runs

These are physical facts, not opinions. Single value per run.

## Derived "primary rating" logic

For filtering ("show me Class IV runs") and display:

```python
def primary_rating(run):
    expert_sources = ["mcquoid", "aw", "wg", "awetstate"]
    candidate_ratings = get_ratings(run, source_codes=expert_sources,
                                     flow_context="normal")
    # Use the median modal rating from expert sources
    return median([r.rating_modal for r in candidate_ratings])
```

For Class III runs, include outfitter sources in the median. For Class V runs, weight McQuoid heavier or use McQuoid alone.

**Always surface the dispute.** Even when filtering returns a single rating, the UI should indicate if the sources disagree by more than one class step.

## Seeding from the curated docs

The `docs/class-III.md`, `docs/class-IV.md`, `docs/class-V.md` files are the best seed data. They already incorporate the cross-reference work. Suggested seeding approach:

1. Extract "Comprehensive list" runs into `runs` table with structural fields (mileage, gradient, put-in/take-out text)
2. Extract tier classifications into `run_classifications`
3. Extract rating quotes from the "Confidence notes" and "Rating disputes" sections into `ratings` with source attribution
4. Leave `rapids`, `hazards`, `flow_windows` empty initially — these will be populated by a second pass pulling from AW, cacreeks, and the curated docs' rapid mentions

A parser for the markdown docs is probably the right first tool to build.

## Tables NOT to build (yet)

- **`paddlers`, `trip_reports`, `reviews`**: only if the app becomes social. Don't build social features into the schema prematurely.
- **`gauge_readings`**: real-time flow data. Just link to Dreamflows/USGS from `flow_windows.gauge_url`; don't mirror the data.
- **`images`, `videos`**: nice-to-have, add when the app has a visual design.

## Migration strategy

Use a proper migration tool from day one: `sqlx`-migrate for Rust, `alembic` for Python, `knex`/`drizzle` for TypeScript, etc. Do not edit production schemas manually. The data is the product; guard it.

## Choice of database engine

Recommended: **SQLite with a Litestream backup**, or **Postgres**.

- SQLite: simpler, file-based, great for personal/single-user app. Full text search via FTS5 is excellent for run names and notes. Arrays can be JSON columns.
- Postgres: overkill for personal use but trivial if the app ever grows. Native array support, PostGIS if you want spatial queries ("runs within 200 miles of Rocklin").

Start SQLite. Migrate to Postgres later if needed — the schema is compatible with minor syntax adjustments.

## First queries to support

The app MVP should answer these:

1. "Show me all Class III-IV runs within 3 hours of Rocklin"
2. "What's running this week?" (requires gauge integration, future)
3. "Show the rating disputes for run X" (transparency)
4. "What runs match: drainage=American, class=IV, dam-released=true?"
5. "What's the progression from Chamberlain Falls?" (requires a `prerequisites` or `similar_runs` concept, future)
6. "Show me overnight options at Class III" (`trip_formats`)

Design the schema around these queries and it'll hold up.
