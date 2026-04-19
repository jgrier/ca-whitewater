# Rating Disputes

Runs where sources genuinely disagree, and why. These are the cases the database schema must handle — never collapse to a single rating.

Format: each entry notes the disputed run, the positions with citations, the underlying cause of disagreement, and the suggested default framing.

---

## NF Feather — Tobin (Cresta Dam → Poe Dam, 6.5 mi)

### Positions

| Source | Rating | Notes |
|---|---|---|
| Darin McQuoid | **V** | Explicit in personal list ("Cresta IV Tobin V") |
| awetstate.com | **IV** | "Not as hard as Stanley and Holbek made it out to be" but sieves make swims catastrophic |
| Holbek & Stanley (1998) | **III-V** | Original rating |
| riverfacts.com | **III-V** | Inherits Holbek/Stanley |

### Why sources disagree

Rounded boulder geology creates sieves and underwater tunnels that are consequence-heavy without being technically difficult to navigate. McQuoid weights consequence into the rating (V); awetstate weights technical difficulty (IV) but warns about consequences separately.

### Default framing

**Treat as V for planning purposes, IV for skill assessment.** A III+/IV kayaker with strong consequences awareness can run it; a V-rated paddler should not be surprised by it. Database: store both positions.

---

## MF Feather — Bald Rock Canyon (Milsap → Oroville, 6.5 mi)

### Positions

| Source | Rating |
|---|---|
| AW / Whitewater Guidebook / Holbek-Stanley | **V+** |
| liquidlore.com | **IV+/V** |
| McQuoid | **V (P)** |
| National Rivers Project | **V+ with 1 mandatory portage** |

### Why sources disagree

The whitewater itself is solid V; the V+ framing is anchored on Atom Bomb Falls being mandatory-portage. If you count the portage as the rating, it's V+; if you count what you actually paddle, it's V.

### Default framing

**V with one mandatory V+ portage.** Everyone can paddle the same water; the question is whether you rate a run by what you paddle or by the hardest thing en route.

---

## Lower Kern — Miracle Hot Springs → Democrat Dam (~12 mi)

### Positions

- Commercial outfitters: **IV** ("the Miracle Run")
- Paper ratings (cacreeks, Whitewater Guidebook, Sierra South): **IV**
- What's actually there: IV whitewater **+ Royal Flush V+ mandatory portage**

### Why it's a problem

My v1 draft incorrectly called this a "Class III classic" because "Lower Kern" is ambiguously used in marketing to cover multiple sections. There are actually two distinct Lower Kern runs:

- **Jungle Run** (Keysville → Miracle Hot Springs, ~6–7 mi): the genuine III Lower Kern
- **Miracle → Democrat** (~12 mi): IV with V+ portage — **not a III run**

### Default framing

**Two separate runs in the database.** Jungle Run = Class III. Miracle → Democrat = Class IV with mandatory V+ portage. Do not conflate.

---

## Merced — El Portal → Briceburg / McClure

### Positions

- Whitewater Guidebook: **Class IV** (28 mi, 34 fpm)
- Whitewater Voyages: "mostly Class III with a few Class IV sections depending on water levels"
- Commercial reality at normal flow: IV
- Contains: Ned's Gulch / Split Rock (**Class V**)
- At high flow (>3500 cfs): the whole thing rises to IV+

### Default framing

**III+ at low flow / IV at normal flow / IV+ at high flow, contains one Class V (Ned's Gulch, often portaged).** Flow-dependent rating stored in `flow_windows` + `ratings`.

---

## Cal Salmon — Nordheimer (Nordheimer CG → Somes Bar, 10.2 mi)

### Positions

- cacreeks: **Class IV+ with 3 class V rapids**
- Whitewater Guidebook: **Class V**
- Commercial framing: "step-up from IV"
- Whitewater Guidebook elsewhere: "good introduction to Class V rowing"

### Why it's a problem

3 of the rapids are unambiguous V (Cascade, Last Chance, Freight Train). But between them is a lot of IV. If you can portage the 3 Vs, it's a IV trip; if you're running them, it's V.

### Default framing

**Class V run with 3 mandatory-scout V rapids.** Do not market/label as "IV step-up" in the database — that framing has killed people.

---

## Klamath — Hell's Corner (Happy Camp → Coon Creek, 18 mi)

### Positions

- Paper rating: **III+ (IV)**
- At normal summer flow (~1500 cfs): III+
- When both Keno Dam turbines running (~3000 cfs): solid IV
- At release event (~3000+ cfs): IV

### Default framing

**III+ at normal flow, IV at high flow.** Include both in `ratings` with `flow_context`.

---

## Upper Kern — Johnsondale → PH #3 / Limestone run (~17 mi)

### Positions

Per Sierra South (authoritative for Kern system): "Below about 1500 CFS many boaters consider the run to be about class III+ or IV-. In the 1500-2500 range, it's about class IV, increasing to IV+ above about 2500 CFS."

### Default framing

**Flow-parameterized rating.** This is the cleanest example of why `flow_windows` table is necessary:
- cfs < 1500: III+ / IV-
- 1500–2500 cfs: IV
- \> 2500 cfs: IV+

---

## NF Yuba — Goodyears Bar → Hwy 49 (~8.5 mi)

### Positions

- Holbek-Stanley era: IV
- Modern: **IV, sometimes with wood-driven V portages**

### Why it's a problem

Wood accumulation year-over-year changes the actual rating. The paper rating is IV; lived experience varies with the winter.

### Default framing

**Class IV with year-specific wood status.** Good case for a `hazards` table with `as_of_date`.

---

## Tuolumne Main (Meral's Pool → Ward's Ferry, 18 mi)

### Positions

- Whitewater Guidebook / AW / OARS / every commercial operator: **IV+**
- At 700–1000 cfs: IV+
- At 2500+ cfs: V territory at Clavey Falls

### Default framing

**IV+ at normal flows, V at high water.** Not really a "disputed" rating so much as a flow-dependent one. Flagged here because it's often cited as a "CA classic Class IV" without the flow caveat.

---

## SF American — Chili Bar run

### Positions

- Paper: **III+**
- At summer normal release (~1200 cfs): III
- At high water (3000+ cfs): III+ / IV- feel

### Default framing

**III at normal flow, III+ at moderate, IV- feel at high water.** Not a true dispute; just flow-dependent.

---

## Goodwin Canyon (Stanislaus below Goodwin Dam, ~4 mi)

### Positions

- All-Outdoors Rafting: **IV+**
- Whitewater Voyages: "IV+"
- riverfacts/Holbek-Stanley: **III-IV(V)**
- McQuoid era kayakers: **IV with Mr. Toad's Wild Ride being IV+/V**

### Default framing

**IV+ with one V rapid (Mr. Toad's Wild Ride).** The `(V)` in the paper rating is Mr. Toad's; it's mandatory-scout and often run.

---

## Generation / consequence disputes worth flagging

These runs see rating drift due to boat technology or changing community expectations:

- **Chamberlain Falls (NF American)**: rated IV+ historically, but awetstate notes it's "a classic class III+/IV- (at low flows, cept for Bogus) to IV (at flows greater than 900)" in modern boats.
- **Hospital Rock (Kaweah)**: Holbek-Stanley called it "not a classic"; modern consensus (McQuoid, liquidlore) treats it as a must-do V.
- **NF Smith**: paper IV; at high flow (winter rainstorm), easily V due to holes and remoteness.

---

## Rule for the database

For each disputed run:
1. Store each source's position separately in `ratings` with `source_id` and `as_of_date`
2. If flow-dependent, use `flow_windows` with rating variations
3. Surface the dispute in UI — do not collapse to a single number
4. When computing a "primary rating" for filtering/search, use the median of expert-kayaker sources (AW, McQuoid, WG, awetstate), not commercial outfitters

This is the whole reason the project exists. Don't compromise it to save a column.
