# Sources

Authoritative sources for California whitewater runs, with trust weights, coverage notes, and biases.

## Primary sources (data origin)

### riverfacts.com
- **URL**: https://www.riverfacts.com/states/ca.html
- **Coverage**: ~267 CA runs; closest thing to a complete enumeration
- **Origin**: Derived from Holbek & Stanley's *The Best Whitewater in California* catalog
- **Trust — sport (III/IV)**: Medium. Ratings mostly accurate but often dated.
- **Trust — expert (V/V+)**: Low-medium. Wood/hazard evolution has outpaced the underlying ratings.
- **Bias**: 1988–98 era; kayaker-first framing; under-represents newer discoveries; doesn't reflect modern-boat rating drift
- **Use for**: Initial enumeration, finding named runs, mileage/gradient, put-in/take-out identification

### Holbek & Stanley, *The Best Whitewater in California* (book)
- **ISBN**: 978-0961152406 (3rd edition, 1998)
- **Coverage**: 180 CA runs, kayaker-perspective
- **Trust — sport**: High where current
- **Trust — expert**: High for historical context; read with date awareness
- **Bias**: Pre-modern-boat; pre-most-recent wood/channel changes; under-covers creeks discovered post-1998 (notably South Silver)
- **Quote from community**: "If Holbek/Stanley says class V, it's the real deal" (Mountain Buzz)

### Cassady & Calhoun, *California White Water: A Guide to the Rivers*
- **ISBN**: 978-0961365028
- **Coverage**: ~50 best runs, rafter-leaning
- **Trust — sport**: High
- **Trust — expert**: Medium (rafter framing)
- **Accessibility**: Print only. Excerpts on tuolumne-river.com, merced-river.com, kaweah-river.com
- **Use for**: Rafter-perspective sanity check, mile-by-mile rapid descriptions

## Curated / editorial sources

### American Whitewater (AW)
- **URL**: https://www.americanwhitewater.org/content/River/view/river-index/state/USA-CAL
- **Coverage**: Comprehensive, community-maintained
- **Trust — sport**: High
- **Trust — expert**: High
- **Accessibility**: Requires JavaScript; no open API. Individual river pages at `/content/River/detail/id/<id>/`
- **Unique value**: Trip reports, gauge integration, FERC relicensing coverage, release schedule coordination
- **Use for**: Current conditions, release dates, authoritative community ratings, dam-release negotiation context (Mokelumne, Fordyce, Yuba system, NF Feather)

### Whitewater Guidebook (Zach Collier)
- **URL**: https://www.whitewaterguidebook.com/california/
- **Coverage**: Curated best-of, rafter/kayaker hybrid framing
- **Trust — sport**: High
- **Trust — expert**: High
- **Bias**: PNW-anchored author; Oregon-leaning; excellent but not CA-native
- **Use for**: Mile-by-mile rapid descriptions, clean curated lists, "California Rowing Progression" logic

### cacreeks.com (Bill Tuthill)
- **URL**: https://www.cacreeks.com/ — run pages at `/{shortname}.htm`
- **Coverage**: Broad, kayaker-native
- **Trust — sport**: High
- **Trust — expert**: High
- **Bias**: Author stopped major updates around 2012–2015 for some runs
- **Unique value**: Accurate gradient, mileage, gauge identification, flow ranges
- **Use for**: Technical specs, gauge relationships, flow windows

## Expert kayaker sources (V/V+ authority)

### Darin McQuoid (darinmcquoid.com)
- **URL**: https://darinmcquoid.com/
- **Coverage**: Expert V/V+ runs across CA and globally
- **Trust — expert**: Highest authority for CA expert ratings
- **Unique value**: Personal rating list at http://jscreekin.blogspot.com/ (also mirrored on his site) with kayaker-honest ratings that differ from outfitter/guidebook framings
- **Bias**: Modern-boat, elite-kayaker perspective; ratings may under-estimate difficulty for intermediate paddlers
- **Use for**: V/V+ arbitration, identifying runs where commercial or guidebook ratings are misleading

### awetstate.com
- **URL**: http://www.awetstate.com/
- **Coverage**: CA kayaker trip reports with mile-by-mile narrative
- **Trust — expert**: High
- **Trust — sport**: High
- **Unique value**: Honest hazard descriptions ("don't come out thinking it is easy class IV" re: Tobin)
- **Use for**: Hazard awareness, modern re-assessment of older guidebook ratings

### liquidlore.com
- **URL**: http://www.liquidlore.com/
- **Coverage**: CA creek-focused expert kayaking
- **Trust — expert**: High
- **Use for**: Cross-check on V ratings (often more realistic than AW "V+" labels)

### Oregon Kayaking
- **URL**: https://www.oregonkayaking.net/
- **Coverage**: PNW + NorCal expert runs
- **Trust — expert**: High
- **Use for**: NorCal / Smith system / Cal Salmon details

### Adventure Sports Journal
- **URL**: https://adventuresportsjournal.com/
- **Coverage**: Feature articles on CA V runs, kayaker profiles
- **Use for**: Context on expedition V, historical first-descent narrative

## Commercial outfitter sources

### Trust level
- **Sport (III/IV)**: Useful. They run these runs commercially, so they know them.
- **Expert (V)**: **Distrust the rating, trust the route info**. Outfitters inflate difficulty ratings to cover liability and to market "adventure." A commercial "V" is often a kayaker IV+.

### Notable outfitters with useful site content
- **OARS** (oars.com) — corporate rafting; cover Tuolumne, MF American, Rogue, etc.
- **Momentum River Expeditions** — Cal Salmon, Forks of the Kern, Upper Klamath
- **Whitewater Voyages** — Kern specialist
- **Trinity River Rafting, Six Rivers Rafting** — Trinity, Pigeon Point
- **All-Outdoors (AO)** — Goodwin Canyon, American forks
- **Sierra Mac** — Cherry Creek commercial operator
- **Kern River Outfitters** — Forks of the Kern, Lower Kern

### Local kayak clubs
- **LA Kayak Club** (losangeleskayakclub.wordpress.com) — authoritative for Kern system put-in/take-out beta
- **Current Adventures, Cal Collective** — Sacramento-area, SF American focus

## Aggregator / meta sources

### Dreamflows
- **URL**: https://www.dreamflows.com/ and cross-listing at `/xlist-ca.php`
- **Use for**: Flow gauge interpretation, release schedules, gauge-to-run mapping
- **Trust**: High for gauges; curates but doesn't rate

### BRT-Insights blog
- **URL**: https://brt-insights.blogspot.com/
- **Coverage**: 257+ CA runs cataloged
- **Trust**: Medium (aggregator; derives from cacreeks/AW)

## Sources NOT to rely on

- **Generic travel blogs** ("snoflo.org", "wizzley.com", "go-nevada.com") — ratings inherited from other sources without verification
- **Outfitter "Class III trips for families"** marketing copy — rating inflation/deflation for sales
- **Single-photo social media posts** — carry no rating context
- **Single YouTube videos** — useful for visual reference, not rating authority

## Provenance rules for the database

Every rating in the database **must** have:
- `source_id` — FK to the sources table
- `as_of_date` — when the source published/updated the rating
- `flow_context` — if applicable (low/normal/high/specific CFS)

If you can't identify the source for a rating, don't ingest it. Provenance is the whole point.
