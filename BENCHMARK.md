How to test & benchmark this (practical)

Think three layers: data checks → logic checks → usefulness checks.

1) Data checks (fast, automatic)

Completeness: no missing lsoa_code, imd2019_decile, crime_rate_per_1k, etc.

Ranges: percent fields in [0,100]; deciles in [1–10]; flags ∈ {yes/no}.

Join sanity: each of the 75 places resolves to an anchor LSOA.

2) Logic checks (does the model behave?)

Monotonicity spot checks:

If asb_trend_12m increases (holding others fixed), lighting score should not go down.

If grime_hotspot_flag=yes, cleanup score should go up.

If % under-18 rises and there’s no nearby youth facility, youth score should go up.

Peer constraints: each place has ≥K peers in the same nation; residuals look centred around 0.

3) Usefulness checks (does it make sense to humans?)

Face validity review: 10% sample of action cards with local colleagues (do the “why here” drivers read true?).

Peer sanity: do the listed peers feel like sensible comparators?

Stability: small changes to weights (±10%) don’t flip #1 and #2 everywhere.

Optional: quantitative benchmarking

Top-1 agreement vs. a simple rules-only baseline (without peers).

Rank correlation (Spearman) between v0.0.2 and a “human-ranked” shortlist from 5–10 towns.

Backtest (if you have past interventions): did places that improved lighting see bigger ASB declines than peers? (Descriptive only at MVP.)