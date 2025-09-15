
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, normalize
from sklearn.neighbors import NearestNeighbors

SIM_FEATURES = [
    "imd2019_decile","pop_density_per_km2","pct_under_18","pct_65_plus","pct_social_rent","asb_trend_12m"
]

def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return (s - s.mean(skipna=True)) / (s.std(ddof=0, skipna=True) or 1.0)

def compute_pip_index(df: pd.DataFrame) -> pd.Series:
    # Components: +Belonging (baseline), +Civic (charities + grants), -ASB rate
    belong = zscore(df.get("belonging_baseline_value"))
    civic = zscore(pd.to_numeric(df.get("charities_active_count"), errors="coerce").fillna(0) +
                   pd.to_numeric(df.get("recent_grants_24m_gbp"), errors="coerce").fillna(0))
    asb = zscore(df.get("crime_rate_per_1k"))
    pip = 0.4*belong + 0.3*civic + 0.3*(-asb)
    return pip

def constrain_candidates(base_row_series, candidates, nation_series, imd_series, imd_tolerance=2):
    # same nation
    same_nation = nation_series == nation_series.loc[base_row_series.name]
    # ±2 IMD deciles if available
    imd_base = pd.to_numeric(imd_series.loc[base_row_series.name], errors="coerce")
    if pd.notna(imd_base):
        imd_ok = (pd.to_numeric(imd_series, errors="coerce") - imd_base).abs() <= imd_tolerance
    else:
        imd_ok = pd.Series(True, index=imd_series.index)
    mask = same_nation & imd_ok
    mask.loc[base_row_series.name] = False  # exclude self
    return candidates[mask]

def main(seed_dir: str, out_dir: str, k: int = 5):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    places = pd.read_csv(Path(seed_dir) / "places_seed_v0_0_1.csv")
    feats = pd.read_csv(Path(seed_dir) / "features_template_v0_0_2.csv")

    # Join nation for constraints
    df = feats.merge(places[["place","nation"]], on="place", how="left")

    # Compute PIP index (safe even if many blanks)
    df["pip_index"] = compute_pip_index(df)

    # Build similarity matrix with imputation (median) and scaling
    sim_df = df[SIM_FEATURES].copy()
    for c in SIM_FEATURES:
        sim_df[c] = pd.to_numeric(sim_df[c], errors="coerce")
        sim_df[c] = sim_df[c].fillna(sim_df[c].median())

    scaler = StandardScaler(with_mean=True, with_std=True)
    X = scaler.fit_transform(sim_df.values)
    X = normalize(X)  # cosine-friendly

    nbrs = NearestNeighbors(metric="cosine", algorithm="brute").fit(X)

    # For each row, find K nearest among constrained set
    peers_rows = []
    expected_pip = []
    residuals = []
    p75_lifts = []
    imd = df["imd2019_decile"]
    nation = df["nation"]
    pip = df["pip_index"]

    for i in range(len(df)):
        # Candidates constrained
        mask = constrain_candidates(df.iloc[i], pd.Series(True, index=df.index), nation, imd)
        idxs = np.where(mask.values)[0]
        if len(idxs) == 0:
            expected_pip.append(np.nan); residuals.append(np.nan); p75_lifts.append(np.nan)
            continue

        # distances to all, then filter to constrained
        distances, indices = nbrs.kneighbors(X[i:i+1], n_neighbors=min(k+1, len(df)))  # includes self
        order = [j for j in indices[0] if j in idxs][:k]
        # collect peers
        for rank, j in enumerate(order, 1):
            peers_rows.append({
                "place": df.loc[i, "place"],
                "peer_place": df.loc[j, "place"],
                "similarity_score": 1.0 - float(1e-9 if j==i else nbrs.kneighbors_graph(X[i:i+1], n_neighbors=len(df), mode="distance")[0, j]),
                "rank": rank
            })

        # expected pip & residual
        peer_pip = pip.iloc[order].dropna()
        if len(peer_pip) >= 1 and pd.notna(pip.iloc[i]):
            exp = peer_pip.mean()
            resid = pip.iloc[i] - exp
            lift = np.nan
            try:
                p75 = np.percentile(peer_pip, 75)
                lift = max(0.0, p75 - pip.iloc[i])
            except Exception:
                pass
        else:
            exp = np.nan; resid = np.nan; lift = np.nan

        expected_pip.append(exp); residuals.append(resid); p75_lifts.append(lift)

    # Write peers
    peers_df = pd.DataFrame(peers_rows)
    peers_df.to_csv(out_dir / "peers.csv", index=False)

    # Write benchmarks
    bm = pd.DataFrame({
        "place": df["place"],
        "peer_expected_pip": expected_pip,
        "pip_residual": residuals,
        "peer_lift_to_p75": p75_lifts
    })
    bm.to_csv(out_dir / "peer_benchmark.csv", index=False)

    # Also emit features_with_peers
    out_feats = df.copy()
    out_feats["peer_expected_pip"] = expected_pip
    out_feats["pip_residual"] = residuals
    out_feats["peer_lift_to_p75"] = p75_lifts
    out_feats.to_csv(out_dir / "features_with_peers.csv", index=False)

    print(f"Wrote {out_dir/'peers.csv'}, {out_dir/'peer_benchmark.csv'}, {out_dir/'features_with_peers.csv'}.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed_dir", default="data/seed")
    ap.add_argument("--out_dir", default="data/processed")
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()
    main(args.seed_dir, args.out_dir, args.k)
