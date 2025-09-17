
# GROUP 6

# xPIP Uplift Engine — MVP v0.0.2

Slides:

https://docs.google.com/presentation/d/1c1icu7oGP3CPz8ysqedPj2kunHPgGwNa2bkf5SxJVqI/edit?usp=sharing

**xPIP** (experimental *Pride in Place* uplift engine) is a lean, explainable recommender for local action.  
It ingests small-area context (LSOA-level) for the **75 Plan for Neighbourhoods towns**, builds a simple
**as‑is nowcast** and a compact **PIP index**, then recommends **three practical interventions** (lighting upgrades,
deep street clean‑ups, youth evening sessions) with named **owners** and a clear “**why here**” rationale.
A lightweight **peer benchmarking** layer finds towns that *look the same on paper* but **overperform**, so we can
copy what’s working.

This repo is scoped to an MVP that’s **deterministic, transparent, and shippable in days**, not months.

---

### Why we chose these three interventions
1) Lighting upgrades
* Owner clarity: LA Highways/Street-lighting (+ DNO for supply).
* Lead time: weeks; procurement often in place; deployable at small scale.
* Data readiness: we can infer gaps/need with simple proxies (ASB trend, night-safety perception, lighting flags).
* Mechanism: improves perceived safety & guardianship on key desire lines -> boosts belonging and evening use.
* Evaluation ease: before/after lux map + night-time complaints + ASB trend.

2) Deep street clean-ups (grime/graffiti blitz)
* Owner clarity: LA cleansing contracts/BID ops.
* Lead time: days–weeks; low capex; repeatable.
* Data readiness: easy to flag with analyst checks/complaints logs; obvious visual change.
* Mechanism: visible care -> stronger place attachment & social norms; reduces cues for disorder.
* Evaluation ease: photo audits + complaints + footfall snippets (optional).

3) Youth evening sessions (2×/week)
* Owner clarity: LA youth services / commissioned VCSOs / leisure centres / schools.
* Lead time: weeks; uses existing spaces (schools, community centres).
* Data readiness: age mix and evening-ASB signals guide targeting.
* Mechanism: provides prosocial routine & guardianship at peak hours.
* Evaluation ease: attendance logs + time-window ASB comparison.

Common strengths across the three:
* Clear named owners per place,
* Short lead times and modest budgets,
* Measurable near-term change,
* Replicable across many towns without bespoke engineering.

### What we didn’t include for MVP (and why)
1. Physical realm (deferred)
* CCTV install/upgrade — higher cost, privacy/governance, patchy open data; slower to deliver/evaluate.
* Alley gating / target hardening — legal orders, consultation; slower lead time.
* Façade/shops grants — multi-party private owners; long procurement cycles.
* Pocket parks/greening — planning/maintenance; slower benefits.

2. Social & economic activation
* Markets / events programming — great for belonging, but scheduling/permits & weather introduce noise in v0.0.1.
* Micro-grants for community groups — valuable but needs a grants backend & monitoring we’re not setting up in MVP.
* Street wardens/ambassadors — staffing model, recurrent spend; trickier to evaluate in days.

3. Mobility & regulation
* Traffic calming / roadspace reallocation — design/consultation; longer horizon.
* Licensing tweaks (e.g., late-night economy) — regulatory process; multi-stakeholder negotiations.
Bottom line: we picked levers that are fast, owner-clear, low-capex, and measurable with the data we already have or can collect quickly. Many of the deferred items can come into v0.2–v0.3 once we have the pipeline and governance in place.


## Problem -> Approach (summary)

**Problem.** Stakeholders need **place‑specific, owner‑actionable** steps that improve *belonging* and *perceived safety*
without waiting for heavy data programmes.

**Approach.**

1. **Describe (as‑is):** build a risk‑adjusted **nowcast** of ASB per 1k for the next quarter and a simple **PIP index**
   (Belonging ↑, Civic capacity ↑, ASB ↓).
2. **Compare (peers):** for each town, find near‑twins (same fundamentals) and measure the **residual** vs peers;
   surface **copyable plays** from positive leaders.
3. **Prescribe (action cards):** rank three interventions per town with expected effect bands, why‑here drivers,
   costs, and **owners** (LA Highways/Street‑lighting, Police SNT, BID if present, and DNO for lighting).

> **Nowcast** = a modelled estimate of the **current/near‑term** situation (e.g., “ASB per 1k this quarter”) using the freshest partial data.  
> It’s the baseline we compare actions against (distinct from a long‑range forecast).

---

## MVP scope (locked)

- **Coverage:** 75 towns (Plan for Neighbourhoods).  
  Modelling at **LSOA**; present results at town level using an **anchor LSOA** per town.
- **Outcomes:** `ASB per 1k (next 3 months)` (primary), `Belonging score`, `Civic capacity index`.
- **Interventions:** `lighting_upgrade`, `street_cleanup`, `youth_evening_session`.
- **Owners named per place:** Local Authority (Highways/Street‑lighting), Police **Safer Neighbourhood Team**, **BID** (if any), **DNO** (lighting).
- **Deliverables:** ranked **Action Cards**, a simple **map**, and CSV/GeoJSON outputs.

**Non‑goals (MVP):** live footfall feeds, CCTV integration, formal causal claims, advanced optimisation. Those can land in v0.2+.

---

## Data (deterministic, MVP-only)

This repo ships seed templates only; the pipeline fills them from open sources listed below.

data/
seed/
places_seed_v0_0_1.csv # 75 places (name, LA, region, nation)
owners_template_v0_0_1.csv # owners skeleton (LA filled; Police/DNO/BID blank)
features_template_v0_0_2.csv # LSOA features incl. peer fields
peers_template_v0_0_1.csv # empty: top-K peers per place
peer_benchmark_template_v0_0_1.csv
README_xpip_mvp_v0_0_2.md # seed bundle notes


### Minimal features (per LSOA, per quarter)
`imd2019_decile, pop_density_per_km2, pct_under_18, pct_65_plus, pct_social_rent, crime_rate_per_1k, asb_trend_12m, belonging_baseline_value, lighting_presence_flag, grime_hotspot_flag, youth_facility_within_800m, charities_active_count, recent_grants_24m_gbp`  
Plus peer fields: `pip_index, peer_expected_pip, pip_residual, peer_lift_to_p75`.

### Owners resolver (deterministic)
Input: town -> centroid/postcode -> **Local Authority**, **Police SNT**, **BID** (if any), **DNO** (lighting).  
We resolve these via lookups (see *References*). Trunk roads handled by national bodies (notes retained).

---

## Peer benchmarking (positive deviance)

- Build a **similarity vector** (IMD decile, pop density, %<18, %65+, % social rent, ASB trend).  
- Find **K nearest peers** (cosine), constrained to **same nation** and **±2 IMD deciles**.  
- Compute `peer_expected_pip` and `pip_residual`.  
- Classify **positive leaders** (≥ +1 SD) and **opportunity towns** (≤ −1 SD).  
- Translate differences in **copyable signals** (lighting presence, grime, youth facility, recent grants) into the 3 interventions.

**Amplifier.** “Among towns like you, the leaders have **good lighting and regular deep cleans**; you lack **good lighting** -> do that first.”  
**Guardrail.** If our scoring suggests **youth sessions** but peers consistently win on **lighting**, we flag it for human review / re‑ranking.

---

## Outputs

- `processed/predictions.csv` — baseline ASB, PIP index, 3 intervention scores, top drivers.  
- `processed/owners.csv` — resolved owners per town.  
- `processed/peers.csv`, `processed/peer_benchmark.csv`.  
- `processed/map.geojson` — polygons + core fields.  
- `action_cards/PLACE_ACTION.md` — one per (town × intervention).

**Action Card (MVP):**
- **What:** the intervention + specific segment/area  
- **Expected effect band:** e.g., “ASB per 1k likely ↓ 5–12% (moderate confidence)”  
- **Why here (drivers):** top 3 moderators + **Peer insight** panel  
- **Owners:** names/links (LA, SNT, BID, DNO)  
- **Cost & lead‑time:** coarse band; **First 3 steps** playbook

---

## Quickstart

```bash
# 1) Clone + set up
git clone https://github.com/decentration/xpip-uplift-engine
cd xpip-uplift-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # (to be added: pandas, numpy, scikit-learn, lightgbm, shap, geopandas, or-tools)

# 2) Drop open data into data/raw/ (see References).

# 3) Run the notebooks / scripts in order
jupyter lab
# 01_build_features.ipynb -> fills features_template
# 02_peer_finder.ipynb    -> peers + residuals
# 03_cards.ipynb          -> generates action_cards and map.geojson
```

## MacOs

```bash
# from your repo root
python3 --version          # check it exists
which python3              # see its path

python3 -m venv .venv      # create venv
source .venv/bin/activate  # activate (zsh)
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python run_mvp.py

```


## Roadmap

- v0.2: add simple uplift learners (T‑learner + SHAP), budget‑aware portfolio selection, optional footfall/CCTV where available.

- v0.3: RCT/stepped‑wedge evaluation hooks, data quality dashboards, fairness monitoring.

- v0.4: richer intervention catalogue, automated owner contacts.

## Ethics, bias & limits

- Small‑area stats can be volatile; we smooth trends and disclose uncertainty.

- Peers guide prioritisation, not blame. Human review remains essential.

- We avoid sensitive individual‑level data; everything here is place‑level and open‑data‑sourced.


## References (open sources to populate the templates)

- Plan for Neighbourhoods – 75 places list (Place–LA–Region): GOV.UK prospectus.

- LSOA 2021 boundaries & definitions: Office for National Statistics (ONS) Geoportal; Census 2021 geographies.

- English Indices of Deprivation 2019 (LSOA): GOV.UK statistical release & File 7 (ranks/deciles).

- Community Life Survey (Belonging question wording – SBeNeigh): DCMS CLS questionnaire/appendix.

- Police street‑level data & neighbourhood lookup: data.police.uk API (with location anonymisation caveat).

- High streets (GB) geometry: ONS/OS “High streets in Great Britain” (GB), and GLA high street boundaries (London).

- Civil society activity & grants: Charity Commission register; 360Giving (GrantNav/API).

- Distribution Network Operator (DNO) finder: Energy Networks Association postcode finder; Ofgem guidance.

- Highways/Street‑lighting responsibility: Local Authority responsibilities (trunk road exceptions).


## Post MVP data points:

- Street lighting asset data: column locations, outages, lamp type/age; post-works lux readings.

- FixMyStreet / council service logs: grime, graffiti, lighting faults, fly-tipping.

- Footfall counts: simple sensors (bidirectional counters), or anonymised Wi-Fi/Bluetooth counts around high streets.

- Retail/occupancy mix: active units vs. vacancies along the high street.

- Youth facility locators: exact opening hours, evening coverage.

- Transport stops & night timetable density: bus stops within 400–800m running after 9pm.

- CCTV presence / fields of view: where published by councils/BIDs.

- Event/activity calendars: frequency of markets, community events.

- OpenStreetMap geometry: cut-throughs/alleys (passages) that correlate with night-time journeys.

- Environmental sensors: noise after dark, light levels.