
import pandas as pd
import argparse
from pathlib import Path

def main(seed_dir: str, out_path: str, la_url_mapping: str | None):
    places = pd.read_csv(Path(seed_dir) / "places_seed_v0_0_1.csv")
    owners = pd.read_csv(Path(seed_dir) / "owners_template_v0_0_1.csv")

    # Optional mapping file for canonical LA URLs (user-populated)
    la_urls = None
    if la_url_mapping and Path(la_url_mapping).exists():
        la_urls = pd.read_csv(la_url_mapping)
        # expected columns: local_authority, highways_owner_url, street_lighting_owner_url
        owners = owners.merge(la_urls, how="left", on="local_authority")
    else:
        owners["highways_owner_url"] = ""
        owners["street_lighting_owner_url"] = ""

    # Police SNT, DNO, BID are left blank for now (to be filled by API resolvers)
    cols = [
        "place","local_authority","nation",
        "highways_owner_name","highways_owner_url",
        "street_lighting_owner_name","street_lighting_owner_url",
        "police_force_name","police_neighbourhood_team_url",
        "dno_operator","bid_name","bid_url","other_owners_notes"
    ]
    owners = owners[cols]
    owners.to_csv(out_path, index=False)
    print(f"Wrote {out_path} ({len(owners)} rows).")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed_dir", default="data/seed", help="Directory with seed CSVs")
    ap.add_argument("--out", default="data/processed/owners_resolved.csv")
    ap.add_argument("--la_url_mapping", default=None, help="Optional CSV mapping LA → canonical URLs")
    args = ap.parse_args()
    main(args.seed_dir, args.out, args.la_url_mapping)
