
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import textwrap

# Simple safety helpers
def num(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

def boolish(x): # interpret various inputs as boolean
    if isinstance(x, str):
        x = x.strip().lower()
        return x in ("1","true","yes","y","t")
    return bool(x)

def clamp01(v): 
    return max(0.0, min(1.0, v))

def scale01(series):
    s = pd.to_numeric(series, errors="coerce")
    if s.max(skipna=True) == s.min(skipna=True):
        return s.fillna(0).apply(lambda _: 0.5)
    return (s - s.min(skipna=True)) / (s.max(skipna=True) - s.min(skipna=True))

def main(seed_dir: str, processed_dir: str, out_cards: str):
    seed_dir = Path(seed_dir); processed_dir = Path(processed_dir); out_dir = Path(out_cards)
    out_dir.mkdir(parents=True, exist_ok=True)

    places = pd.read_csv(seed_dir / "places_seed_v0_0_1.csv")
    owners = pd.read_csv(processed_dir / "owners_resolved.csv")
    feats = pd.read_csv(processed_dir / "features_with_peers.csv")
    peers = pd.read_csv(processed_dir / "peers.csv")

    # Join owners onto feats
    df = feats.merge(owners, on=["place"], how="left", suffixes=("","_own"))

    # Heuristic scores (0..100)
    asb_trend = scale01(df.get("asb_trend_12m"))
    crime_level = scale01(df.get("crime_rate_per_1k"))
    u18 = scale01(df.get("pct_under_18"))
    civic_low = 1 - scale01(df.get("charities_active_count"))
    belong_low = 1 - scale01(df.get("belonging_baseline_value"))
    no_light = (~df.get("lighting_presence_flag").astype(str).str.lower().isin(["1","true","yes","y","t"])).astype(float)
    grime = df.get("grime_hotspot_flag").astype(str).str.lower().isin(["1","true","yes","y","t"]).astype(float)
    no_youth = (~df.get("youth_facility_within_800m").astype(str).str.lower().isin(["1","true","yes","y","t"])).astype(float)

        # (vector removed; compute row-wise later)

    # Peer insights: for each place, examine peers' copyable signals
    peer_groups = peers.merge(df[["place","lighting_presence_flag","grime_hotspot_flag","youth_facility_within_800m","pip_index"]], 
                              left_on="peer_place", right_on="place", how="left", suffixes=("","_peer"))
    insights = {}
    for place, g in peer_groups.groupby("place"):
        total = len(g)
        if total == 0:
            insights[place] = []
            continue
        # positive leaders = top half by pip_index among peers
        g = g.sort_values("pip_index", ascending=False)
        leaders = g.head(max(1, total//2))
        msgs = []
        def share_true(series):
            s = series.astype(str).str.lower().isin(["1","true","yes","y","t"]).mean()
            return float(s) if not np.isnan(s) else 0.0

        if share_true(leaders["lighting_presence_flag"]) >= 0.6:
            msgs.append("Peers that perform best mostly **have adequate lighting** on key routes.")
        if (1 - share_true(leaders["grime_hotspot_flag"])) >= 0.6:
            msgs.append("Top peers **do routine deep cleans** and avoid visible grime/graffiti.")
        if share_true(leaders["youth_facility_within_800m"]) >= 0.6:
            msgs.append("Top peers **run evening youth provision** within easy reach.")
        insights[place] = msgs

    # Compose action cards (top 3 ranked)
    for i, row in df.iterrows():
        asb_t = float(asb_trend.iloc[i]) if not pd.isna(asb_trend.iloc[i]) else 0.0
        crime_t = float(crime_level.iloc[i]) if not pd.isna(crime_level.iloc[i]) else 0.0
        u18_t = float(u18.iloc[i]) if not pd.isna(u18.iloc[i]) else 0.0
        civic_low_t = float(civic_low.iloc[i]) if not pd.isna(civic_low.iloc[i]) else 0.0
        belong_low_t = float(belong_low.iloc[i]) if not pd.isna(belong_low.iloc[i]) else 0.0
        no_light_t = float(no_light.iloc[i]) if not pd.isna(no_light.iloc[i]) else 0.0
        grime_t = float(grime.iloc[i]) if not pd.isna(grime.iloc[i]) else 0.0
        no_youth_t = float(no_youth.iloc[i]) if not pd.isna(no_youth.iloc[i]) else 0.0
        lighting_score_val = 100 * clamp01(0.45*asb_t + 0.25*crime_t + 0.15*belong_low_t + 0.15*no_light_t)
        cleanup_score_val  = 100 * clamp01(0.55*grime_t + 0.25*crime_t + 0.20*civic_low_t)
        youth_score_val    = 100 * clamp01(0.50*u18_t + 0.30*crime_t + 0.20*no_youth_t)
        place = row['place']
        

        place = row["place"]
        scores = [
            ("lighting_upgrade", float(lighting_score_val)),
            ("street_cleanup", float(cleanup_score_val)),
            ("youth_evening_session", float(youth_score_val))
        ]
        scores.sort(key=lambda x: x[1], reverse=True)

        drivers = []
        if asb_trend.iloc[i] > 0.6: drivers.append("ASB trend is **rising**")
        if crime_level.iloc[i] > 0.6: drivers.append("Overall crime is **high** for peers")
        if belong_low.iloc[i] > 0.6: drivers.append("Belonging sentiment baseline is **low**")
        if no_light.iloc[i] > 0.6: drivers.append("Lighting coverage appears **weak** on key segments")
        if grime.iloc[i] > 0.6: drivers.append("Visible **grime/graffiti hotspots** present")
        if u18.iloc[i] > 0.6: drivers.append("High share of **under‑18s**")
        if no_youth.iloc[i] > 0.6: drivers.append("Gap in **nearby youth provision**")

        owner_lines = [
            f"- **Highways/Street lighting:** {row.get('highways_owner_name','')}",
            f"- **Police SNT:** {row.get('police_force_name','')}",
            f"- **BID:** {row.get('bid_name','') or '—'}",
            f"- **DNO (lighting):** {row.get('dno_operator','')}",
        ]

        peer_panel = insights.get(place, [])
        peer_text = "\n".join([f"- {m}" for m in peer_panel]) if peer_panel else "—"

        # Markdown
        drivers_text = ("\n- " + "\n- ".join(drivers)) if drivers else "—"
        md = f"""---
place: {place}
version: xpip-mvp-0.0.2
---

# Action Plan — {place}

## Ranked picks
1) **{scores[0][0]}** — score: {scores[0][1]:.1f}
2) **{scores[1][0]}** — score: {scores[1][1]:.1f}
3) **{scores[2][0]}** — score: {scores[2][1]:.1f}

## Why here (signals)
{drivers_text}

## Owners (delivery)
{chr(10).join(owner_lines)}

## Peer insight
{peer_text}

## First 3 steps (playbook)
- Scope exact segment(s) and confirm on-the-ground constraints
- Engage owners above; confirm lead-time and cost band
- Set before/after checks (simple photo/lux map or attendance and time-window ASB trend)
"""
        out_path = Path(out_dir) / f"{place.replace(' ','_').replace('/','-')}_action_plan.md"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)

    print(f"Wrote action cards to {out_dir}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed_dir", default="data/seed")
    ap.add_argument("--processed_dir", default="data/processed")
    ap.add_argument("--out_cards", default="action_cards")
    args = ap.parse_args()
    main(args.seed_dir, args.processed_dir, args.out_cards)
