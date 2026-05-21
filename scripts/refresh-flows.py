#!/usr/bin/env python3
"""Refresh app/flows.js from Dreamflows realtime CSV (+ USGS for freshness).

Dreamflows aggregates USGS, CDEC, and agency-supplied feeds into one CSV
keyed by their internal RiverId (the NNN in `dreamflows.com/graphs/day.NNN.php`).
Using that as the primary source avoids per-CDEC-station code guessing and
gives us coverage for runs whose USGS gauges were discontinued at WY2025 end.

Runs the script server-side, so no CORS issues. The HTML reads flows.js
directly via <script src=…> (no fetch needed, works from file://).
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

DREAMFLOWS_CSV = "https://www.dreamflows.com/realtime.csv.php"
USGS_BATCH = "https://waterservices.usgs.gov/nwis/iv/?sites={sites}&parameterCd=00060&format=json"

# Each run: df_id is the Dreamflows RiverId (zero-padded 3-digit string),
# optional usgs_id for direct USGS reads (fresher than Dreamflows for natural rivers).
# Ranges: cfs below low_min → "white" (too low); low_min..good_min → "yellow"
# (low but runnable); good_min..good_max → "green" (perfect); above good_max → "red".
# Ranges are per class context — same river can have different ranges for II vs IV.
GAUGE_MAP: dict[str, dict] = {
    # ===== CLASS II =====
    "lower-american-ii":          {"df_id":"076","usgs_id":"11446500","name":"American at Fair Oaks","low_min":800,"good_min":1500,"good_max":4000},
    "ef-carson-overnight-ii":     {"df_id":"127","usgs_id":"10308200","name":"EF Carson near Markleeville","low_min":400,"good_min":700,"good_max":3000},
    "klamath-iron-gate-sarah":    {"df_id":"003","usgs_id":"11516530","name":"Klamath below Iron Gate","low_min":800,"good_min":1200,"good_max":4000},
    "trinity-lewiston-junction":  {"df_id":"008","usgs_id":"11525500","name":"Trinity at Lewiston","low_min":300,"good_min":500,"good_max":2500},
    "mokelumne-electra-ii":       {"df_id":"388","name":"Mokelumne below Electra PH","low_min":450,"good_min":700,"good_max":1500},
    "lower-kern-town-run":        {"df_id":"105","name":"Kern below Isabella","low_min":400,"good_min":800,"good_max":2500},
    "sacramento-redding-anderson":{"df_id":"089","usgs_id":"11370500","name":"Sacramento below Keswick","low_min":3000,"good_min":5000,"good_max":15000},
    "russian-cloverdale-healdsburg":{"df_id":"286","usgs_id":"11463000","name":"Russian near Cloverdale","low_min":250,"good_min":400,"good_max":1500},
    "stanislaus-camp-9-parrotts": {"df_id":"084","name":"Stanislaus at Camp Nine","low_min":500,"good_min":700,"good_max":2000},
    "trinity-junction-burnt-ranch":{"df_id":"255","usgs_id":"11526250","name":"Trinity at Douglas City","low_min":500,"good_min":1000,"good_max":4000},
    "klamath-sarah-happy-camp":   {"df_id":"003","usgs_id":"11520500","name":"Klamath below Iron Gate (proxy)","low_min":1000,"good_min":1500,"good_max":5000},
    "truckee-tahoe-river-ranch":  {"df_id":None,"usgs_id":"10337500","name":"Truckee at Tahoe City","low_min":150,"good_min":300,"good_max":800},
    "cache-creek-upper":          {"df_id":"394","name":"Cache Creek below Clear Lake","low_min":300,"good_min":500,"good_max":2000},
    "smith-jed-smith-mouth":      {"df_id":"001","usgs_id":"11532500","name":"Smith near Crescent City","low_min":1000,"good_min":2000,"good_max":8000},
    "cosumnes-michigan-bar":      {"df_id":"077","usgs_id":"11335000","name":"Cosumnes at Michigan Bar","low_min":500,"good_min":800,"good_max":2000},
    "sf-eel-leggett-piercy":      {"df_id":"024","usgs_id":"11475800","name":"SF Eel at Leggett","low_min":400,"good_min":800,"good_max":4000},
    "bear-river-dog-bar":         {"df_id":"067","name":"Bear at Hwy 174 Bridge","low_min":250,"good_min":500,"good_max":1500},
    "putah-creek-below-monticello":{"df_id":None,"usgs_id":"11454000","name":"Putah Creek near Winters","low_min":300,"good_min":450,"good_max":900},
    "west-carson":                {"df_id":"714","usgs_id":"10310000","name":"W Carson at Woodfords","low_min":150,"good_min":300,"good_max":800},
    "owens-pleasant-valley-bishop":{"df_id":None,"name":"Owens at Pleasant Valley","low_min":150,"good_min":300,"good_max":600},
    "mf-feather-sloat-nelson":    {"df_id":"378","name":"MF Feather below Sloat","low_min":400,"good_min":600,"good_max":2400},
    "van-duzen-grizzly":          {"df_id":"018","usgs_id":"11478500","name":"Van Duzen near Bridgeville","low_min":500,"good_min":1000,"good_max":4000},
    "walker-main-stem":           {"df_id":"140","usgs_id":"10296000","name":"W Walker below L Walker","low_min":250,"good_min":500,"good_max":1200},
    "feather-oroville-thermalito":{"df_id":None,"name":"Feather at Oroville (no df gauge)","low_min":800,"good_min":1500,"good_max":5000},

    # ===== CLASS III =====
    "sf-american-iii":            {"df_id":"075","name":"SF American at Chili Bar","low_min":800,"good_min":1200,"good_max":2500},
    "upper-sac-box-sims-iii":     {"df_id":"040","usgs_id":"11342000","name":"Sacramento at Delta","low_min":700,"good_min":1200,"good_max":3500},
    "truckee-floriston":          {"df_id":None,"usgs_id":"10346000","name":"Truckee at Farad","low_min":400,"good_min":800,"good_max":2500},
    "kings-banzai-iii":           {"df_id":"100","name":"Kings at Rodgers Crossing","low_min":750,"good_min":1500,"good_max":8000},
    "klamath-hells-corner-iii":   {"df_id":"519","usgs_id":"11510700","name":"Klamath below JC Boyle PH","low_min":900,"good_min":1500,"good_max":2500},
    "cache-rumsey":               {"df_id":"587","usgs_id":"11451800","name":"Cache at Rumsey Bridge","low_min":450,"good_min":700,"good_max":3500},
    "trinity-pigeon-point":       {"df_id":"045","usgs_id":"11526250","name":"Trinity above North Fork","low_min":700,"good_min":1500,"good_max":5000},
    "lower-kern-jungle-run":      {"df_id":"105","name":"Kern below Isabella","low_min":400,"good_min":1000,"good_max":2500},
    "mccloud-ah-di-na":           {"df_id":"043","name":"McCloud at Ah-Di-Na","low_min":400,"good_min":600,"good_max":1500},
    "cal-salmon-sf":              {"df_id":"006","usgs_id":"11522500","name":"Salmon at Somes Bar","low_min":800,"good_min":1500,"good_max":3500},
    "sf-eel-big-bend-piercy":     {"df_id":"024","usgs_id":"11475800","name":"SF Eel at Leggett","low_min":800,"good_min":1500,"good_max":6000},
    "main-eel-dos-rios-alderpoint":{"df_id":"022","usgs_id":"11475000","name":"Eel at Fort Seward","low_min":1000,"good_min":2000,"good_max":8000},
    "nf-feather-rock-creek":      {"df_id":"051","name":"NF Feather below Rock Creek Dam","low_min":600,"good_min":800,"good_max":2000},
    "upper-kern-camp-3-limestone":{"df_id":"104","name":"Kern at Kernville","low_min":450,"good_min":800,"good_max":2500},
    "alameda-creek-sunol-niles":  {"df_id":"421","usgs_id":"11179000","name":"Alameda near Niles","low_min":300,"good_min":500,"good_max":1500},
    "nf-american-shirttail":      {"df_id":None,"usgs_id":"11427000","name":"NF American at NF Dam","low_min":400,"good_min":700,"good_max":2000},
    "arroyo-seco":                {"df_id":"239","name":"Arroyo Seco near Greenfield","low_min":150,"good_min":250,"good_max":500},
    "little-sur-river":           {"df_id":"050","usgs_id":"11143000","name":"Big Sur River (proxy)","low_min":300,"good_min":500,"good_max":1500},
    "mad-river-ruth":             {"df_id":None,"usgs_id":"11480390","name":"Mad above Ruth Reservoir","low_min":400,"good_min":700,"good_max":2500},
    "outlet-tomki":               {"df_id":"113","usgs_id":"11473900","name":"Eel below Outlet Creek","low_min":500,"good_min":1200,"good_max":5000},

    # ===== CLASS IV =====
    "nf-american-chamberlain":    {"df_id":None,"usgs_id":"11427000","name":"NF American at NF Dam","low_min":500,"good_min":900,"good_max":2500},
    "mf-american-oxbow-greenwood-iv":{"df_id":"070","name":"MF American Oxbow PH release","low_min":800,"good_min":1200,"good_max":2000},
    "tuolumne-main":              {"df_id":"090","name":"Tuolumne at Meral's Pool","low_min":600,"good_min":2200,"good_max":2800},
    "upper-kern-thunder-run":     {"df_id":"682","name":"Kern below Fairview Dam","low_min":600,"good_min":900,"good_max":2500},
    "lower-kern-miracle-democrat":{"df_id":"105","name":"Kern below Isabella","low_min":600,"good_min":1000,"good_max":3000},
    "kaweah-upper-6":             {"df_id":"103","name":"Kaweah at Three Rivers","low_min":500,"good_min":1000,"good_max":3000},
    "upper-sac-box-gibson":       {"df_id":"040","usgs_id":"11342000","name":"Sacramento at Delta","low_min":500,"good_min":800,"good_max":2500},
    "goodwin-canyon-iv":          {"df_id":"758","name":"Stanislaus Goodwin Dam schedule","low_min":1000,"good_min":1500,"good_max":3000},
    "nf-smith-low-divide":        {"df_id":"162","name":"NF Smith at Gasquet","low_min":500,"good_min":1000,"good_max":4000},
    "sf-smith-gorge":             {"df_id":"164","name":"SF Smith near Hiouchi","low_min":500,"good_min":1000,"good_max":3000},
    "mf-smith-oregon-hole":       {"df_id":"163","name":"MF Smith at Gasquet","low_min":400,"good_min":800,"good_max":2500},
    "nf-yuba-goodyears":          {"df_id":"057","usgs_id":"11413000","name":"N Yuba below Goodyears Bar","low_min":700,"good_min":1000,"good_max":2500},
    "pit-5":                      {"df_id":"049","name":"Pit below Pit 4 Dam (Pit 5 put-in)","low_min":700,"good_min":1000,"good_max":2500},
    "pit-falls":                  {"df_id":"213","usgs_id":"11355010","name":"Pit below Pit 1 PH","low_min":700,"good_min":900,"good_max":1500},
    "merced-el-portal-iv":        {"df_id":"225","name":"Merced below Briceburg","low_min":2000,"good_min":3000,"good_max":5000},
    "sf-yuba-bridgeport":         {"df_id":"065","name":"SF Yuba at Hwy 49 Bridge","low_min":600,"good_min":1000,"good_max":2000},
    "upper-mccloud-fowler":       {"df_id":"043","name":"McCloud at Ah-Di-Na (proxy)","low_min":1000,"good_min":1500,"good_max":3000},
    "nf-mokelumne-tiger":         {"df_id":"385","name":"NF Mokelumne above Tiger Cr Afterbay","low_min":500,"good_min":700,"good_max":1200},
    "sf-yuba-edwards-washington": {"df_id":"065","name":"SF Yuba at Hwy 49 Bridge","low_min":500,"good_min":1000,"good_max":2500},
    "sf-cal-salmon-limestone-matthews":{"df_id":"006","usgs_id":"11522500","name":"Salmon at Somes Bar (proxy)","low_min":2000,"good_min":3000,"good_max":5500},
    "west-walker-rock-garden":    {"df_id":"140","usgs_id":"10296000","name":"W Walker below L Walker","low_min":300,"good_min":500,"good_max":1500},
    "piru-creek":                 {"df_id":None,"usgs_id":"11109550","name":"Piru above Frenchmans Flat","low_min":250,"good_min":500,"good_max":2000},
    "sf-merced-snyder":           {"df_id":"225","name":"Merced below Briceburg (SF proxy)","low_min":1500,"good_min":2500,"good_max":5000},
    "clear-creek-whiskeytown":    {"df_id":"037","usgs_id":"11372000","name":"Clear Creek below Whiskeytown","low_min":200,"good_min":300,"good_max":800},
    "sespe-creek":                {"df_id":"687","usgs_id":"11111500","name":"Sespe near Wheeler Springs","low_min":300,"good_min":600,"good_max":2500},
    "arroyo-valle":               {"df_id":"397","usgs_id":"11176400","name":"Arroyo Valle below Lang Canyon","low_min":300,"good_min":600,"good_max":2000},
    "hayfork-creek":              {"df_id":"013","name":"Hayfork at Hyampom","low_min":700,"good_min":1200,"good_max":3500},
    "upper-sac-box-dunsmuir":     {"df_id":"040","usgs_id":"11342000","name":"Sacramento at Delta (downstream proxy)","low_min":400,"good_min":600,"good_max":1500},

    # ===== CLASS V =====
    "cherry-creek":               {"df_id":"088","name":"Cherry below Holm Powerhouse","low_min":500,"good_min":1000,"good_max":1400},
    "forks-of-the-kern":          {"df_id":"681","name":"Kern above Fairview Dam","low_min":400,"good_min":800,"good_max":3000},
    "mf-feather-devils-canyon":   {"df_id":"054","name":"MF Feather at Milsap Bar","low_min":600,"good_min":1700,"good_max":2300},
    "mf-feather-bald-rock":       {"df_id":"054","name":"MF Feather at Milsap Bar","low_min":400,"good_min":675,"good_max":925},
    "burnt-ranch-gorge":          {"df_id":"009","usgs_id":"11527000","name":"Trinity near Burnt Ranch","low_min":500,"good_min":1000,"good_max":3000},
    "cal-salmon-nordheimer":      {"df_id":"006","usgs_id":"11522500","name":"Salmon at Somes Bar","low_min":700,"good_min":1200,"good_max":3500},
    "giant-gap-nf-american":      {"df_id":None,"usgs_id":"11427000","name":"NF American at NF Dam","low_min":700,"good_min":1000,"good_max":2500},
    "fordyce-creek":              {"df_id":"063","name":"Fordyce below Fordyce Dam","low_min":200,"good_min":300,"good_max":500},
    "kaweah-hospital-rock":       {"df_id":"103","name":"Kaweah at Three Rivers","low_min":400,"good_min":800,"good_max":1500},
    "dinkey-creek":               {"df_id":"454","name":"Dinkey Creek at Dinkey Meadow","low_min":150,"good_min":300,"good_max":500},
    "royal-gorge-nf-american":    {"df_id":None,"usgs_id":"11427000","name":"NF American at NF Dam (downstream proxy)","low_min":700,"good_min":900,"good_max":1500},
    "upper-kings-garlic-falls":   {"df_id":"100","name":"Kings at Rodgers Crossing","low_min":800,"good_min":1200,"good_max":2000},
    "middle-kings":               {"df_id":"100","name":"Kings at Rodgers Crossing (proxy)","low_min":700,"good_min":1200,"good_max":2500},
    "sf-american-golden-gate":    {"df_id":"184","name":"SF American below Kyburz","low_min":500,"good_min":700,"good_max":1500},
    "sf-american-slab-creek-v":   {"df_id":"074","name":"SF American below Slab Creek Dam","low_min":1000,"good_min":1400,"good_max":1600},
    "rubicon":                    {"df_id":"684","name":"Rubicon below Rubicon Dam","low_min":500,"good_min":700,"good_max":1500},
    "nf-mokelumne-devils-nose":   {"df_id":"384","name":"NF Mokelumne below Salt Springs","low_min":700,"good_min":900,"good_max":1500},
    "south-silver-creek":         {"df_id":"699","name":"South Silver above Ice House","low_min":80,"good_min":110,"good_max":200},
    "nf-stanislaus-boards-v":     {"df_id":"133","name":"NF Stanislaus at Avery","low_min":1200,"good_min":1400,"good_max":2000},
    "mf-stanislaus-sandbar-camp-9":{"df_id":"083","name":"MF Stanislaus below Sandbar","low_min":600,"good_min":1700,"good_max":2300},
    "nf-feather-tobin-v":         {"df_id":"759","name":"NF Feather below Belden Dam","low_min":1500,"good_min":2000,"good_max":3500},
    "dry-meadow-teacups":         {"df_id":"778","name":"Dry Meadow Creek above Kern","low_min":60,"good_min":100,"good_max":250},
    "brush-creek":                {"df_id":"779","name":"Brush Creek above Kern","low_min":80,"good_min":100,"good_max":250},
    "sf-kings-horseshoe-bend":    {"df_id":"100","name":"Kings at Rodgers Crossing (proxy)","low_min":800,"good_min":1000,"good_max":2500},
    "mf-ef-kaweah":               {"df_id":"363","name":"MF Kaweah above Marble Fork","low_min":300,"good_min":600,"good_max":1200},
    "big-kimshew-creek":          {"df_id":"529","name":"W Br Feather at Whiskey Flat (proxy)","low_min":500,"good_min":750,"good_max":1050},
    "butte-creek":                {"df_id":"123","usgs_id":"11390000","name":"Butte Creek near Chico","low_min":300,"good_min":400,"good_max":1200},
    "sf-cal-salmon-limestone-bluffs":{"df_id":"006","usgs_id":"11522500","name":"Salmon at Somes Bar (proxy)","low_min":2500,"good_min":3500,"good_max":6000},
    "smith-river-gorges-sf-mf":   {"df_id":"001","usgs_id":"11532500","name":"Smith (Jed Smith)","low_min":2000,"good_min":3500,"good_max":9000},
}


def fetch_dreamflows() -> dict[str, dict]:
    """Fetch all Dreamflows CA realtime flows. Returns {df_id: {cfs, raw, ts}}."""
    out: dict[str, dict] = {}
    req = urllib.request.Request(DREAMFLOWS_CSV, headers={"User-Agent": "Mozilla/5.0 (ca-whitewater)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    # CSV is preceded by metadata lines; find the header row
    lines = text.splitlines()
    header_idx = next((i for i, l in enumerate(lines) if l.startswith("RiverId,")), -1)
    if header_idx < 0:
        raise RuntimeError("Could not find CSV header in Dreamflows output")
    reader = csv.DictReader(io.StringIO("\n".join(lines[header_idx:])))
    for row in reader:
        df_id = row["RiverId"].strip()
        if not df_id:
            continue
        flow_raw = row.get("RiverFlow", "").strip()
        date = row.get("Date", "").strip()
        time_s = row.get("Time", "").strip()
        ts = f"{date} {time_s}" if date else None
        # Parse numeric flow
        cfs: float | None = None
        try:
            cfs = float(flow_raw.replace(",", ""))
        except (ValueError, TypeError):
            cfs = None
        out[df_id] = {"cfs": cfs, "raw": flow_raw, "ts": ts, "unit": row.get("FlowUnit", "").strip()}
    return out


def fetch_usgs_batch(site_ids: list[str]) -> dict[str, dict]:
    """Latest USGS CFS values (instantaneous, every 15-min)."""
    if not site_ids:
        return {}
    out: dict[str, dict] = {}
    url = USGS_BATCH.format(sites=",".join(site_ids))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (ca-whitewater)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        for ts in data.get("value", {}).get("timeSeries", []):
            code = ts["sourceInfo"]["siteCode"][0]["value"]
            vals = ts["values"][0]["value"]
            if not vals:
                continue
            latest = vals[-1]
            try:
                cfs = float(latest["value"])
                if cfs < -1000:  # USGS -999999 sentinel
                    continue
            except (TypeError, ValueError):
                continue
            out[code] = {"cfs": cfs, "ts": latest["dateTime"]}
    except Exception as e:
        print(f"  USGS batch failed: {e}", file=sys.stderr)
    return out


def main():
    repo_root = Path(__file__).resolve().parent.parent
    out_path = repo_root / "app" / "flows.js"

    print("Fetching Dreamflows realtime CSV...")
    try:
        df_data = fetch_dreamflows()
        print(f"  got {len(df_data)} river readings")
    except Exception as e:
        print(f"  FAILED: {e}", file=sys.stderr)
        df_data = {}

    print("Fetching USGS instantaneous values...")
    usgs_ids = sorted({cfg["usgs_id"] for cfg in GAUGE_MAP.values() if cfg.get("usgs_id")})
    print(f"  {len(usgs_ids)} unique USGS sites")
    usgs_data: dict[str, dict] = {}
    for i in range(0, len(usgs_ids), 50):
        usgs_data.update(fetch_usgs_batch(usgs_ids[i:i+50]))
    print(f"  got data for {len(usgs_data)} / {len(usgs_ids)} sites")

    # Build per-run flow dict. Prefer USGS (fresher 15-min instantaneous)
    # for natural rivers; fall back to Dreamflows (hourly, broader coverage).
    # Always include ranges + gauge name so the HTML can render color + tooltip
    # without duplicating the config.
    flows: dict[str, dict] = {}
    df_missing: list[str] = []
    for run_id, cfg in GAUGE_MAP.items():
        record: dict = {
            "name": cfg["name"],
            "low_min": cfg["low_min"],
            "good_min": cfg["good_min"],
            "good_max": cfg["good_max"],
        }
        if cfg.get("df_id"):
            record["link"] = f"https://www.dreamflows.com/graphs/day.{cfg['df_id']}.php"
        if cfg.get("usgs_id") and cfg["usgs_id"] in usgs_data:
            u = usgs_data[cfg["usgs_id"]]
            record["cfs"] = u["cfs"]
            record["ts"] = u["ts"]
            record["src"] = "usgs"
        elif cfg.get("df_id") and cfg["df_id"] in df_data:
            d = df_data[cfg["df_id"]]
            if d["cfs"] is not None:
                record["cfs"] = d["cfs"]
                record["ts"] = d["ts"]
                record["src"] = "dreamflows"
            elif d["raw"]:
                # Non-numeric reading like "Low" — preserve as text
                record["raw"] = d["raw"]
                record["ts"] = d["ts"]
                record["src"] = "dreamflows"
        if "cfs" not in record and "raw" not in record and cfg.get("df_id"):
            df_missing.append(f"{run_id} (df_id={cfg['df_id']})")
        flows[run_id] = record

    print(f"\nGot flow data for {len(flows)} / {len(GAUGE_MAP)} runs")
    if df_missing:
        print(f"\nMissing (df_ids that weren't in CSV): {len(df_missing)}")
        for m in df_missing[:20]:
            print(f"  {m}")
        if len(df_missing) > 20:
            print(f"  ... and {len(df_missing)-20} more")

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "flows": flows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("window.FLOWS = " + json.dumps(payload, indent=2) + ";\n")
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    main()
