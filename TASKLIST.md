# MVP task list (actionable & minimal)
## A) Seed + geocoding

1. Confirm the 75 places (from seed CSV) and choose the anchor LSOA for each (largest overlap with the named high-street segment).

- Inputs: places_seed_v0_0_1.csv

- Output: anchor_lsoa.csv → place,lsoa_code,lsoa_name,anchor=True

2. Attach LSOA metadata (names/codes) to features template.

- Output: populate features_template_v0_0_2.csv cols: lsoa_code,lsoa_name

## B) Deterministic owners

3. Resolve Local Authority owners (already prefilled) + add canonical URLs for Highways/Street Lighting pages.

- Output: owners_resolved.csv (LA names + URLs)

4. Police SNT lookup (centroid → Police.uk neighbourhood; add team URL).

- Output: add police_force_name,police_neighbourhood_team_url to owners_resolved.csv

5. DNO lookup (centroid/postcode → ENA result).

- Output: add dno_operator to owners_resolved.csv

6. BID presence (GLA/London + LA pages elsewhere).

- Output: add bid_name,bid_url (nullable)

## C) Features (MVP-only)

7. IMD join (LSOA → decile).

- Output: fill imd2019_decile

8. Crime/ASB aggregation (Police.uk monthly → rolling 12m & next-quarter nowcast baseline).

- Output: crime_rate_per_1k,asb_trend_12m

9. Civic capacity

- Charity Commission + 360Giving counts/£.

- Output: charities_active_count,recent_grants_24m_gbp,grant_funding_3y_gbp

10. Micro-survey baseline (wording aligned to CLS; tiny pilot if feasible or set neutral priors).

- Output: belonging_baseline_value (or mark NA and use neutral prior)

11. Copyable signals (analyst flags for MVP)

- Simple desk check/OSM for lighting_presence_flag,youth_facility_within_800m; site/StreetView for grime_hotspot_flag.

- Output: fill the three flags + lighting_density_per_km if feasible

## D) Peer layer

12. Compute PIP index (z-score combine: +Belonging, +Civic, −ASB).

- Output: pip_index

13. KNN peers (same nation, ±2 IMD deciles; cosine distance).

- Output: peers.csv (top-5 with similarity score)

14. Peer benchmark (expected PIP, residual, P75 lift).

- Output: peer_benchmark.csv + fill peer_expected_pip,pip_residual,peer_lift_to_p75 in features

## E) Scoring → Action Cards

15. Rule-based intervention scoring (effect-priors + moderators):

- Lighting ↑ where ASB trend high & night-safety low & lighting flag = false

- Clean-up ↑ where grime flag = true & ASB level moderate & civic capacity low

- Youth sessions ↑ where %<18 high & evening ASB signal & youth facility absent/nearby gap

-  Output: predictions.csv (3 scores + top drivers)

16. Peer guardrail (nudge/tie-break using positive-leader patterns).

- Output: adjusted ranking + “peer insight” notes

17. Action Card generation (Markdown) with owners auto-inserted, why here drivers, cost bands & first 3 steps.

- Output: action_cards/{PLACE}_{ACTION}.md

## F) Map + QA

18. Map build (GeoJSON with scores & picks; static web).

- Output: processed/map.geojson + web/map/

19. QA pass (10% sample):

- Owners URLs valid; peers sensible; action rationale reads clearly.

20. Model card & limits note (short):

- Output: MODEL_CARD.md (data sources, methods, limits, ethics)