
#!/usr/bin/env python3
import subprocess, sys, os, pathlib

def run(cmd):
    print("\n>>> " + " ".join(cmd))
    subprocess.check_call(cmd)

def main():
    here = pathlib.Path(__file__).resolve().parent
    os.chdir(here)

    # 1) Resolve owners
    run([sys.executable, "src/owners_resolver/resolve_owners.py",
         "--seed_dir", "data/seed", "--out", "data/processed/owners_resolved.csv"])

    # 2) Peer finder
    run([sys.executable, "src/peers/peer_finder.py",
         "--seed_dir", "data/seed", "--out_dir", "data/processed", "--k", "5"])

    # 3) Generate action cards
    run([sys.executable, "src/cards/generate_action_cards.py",
         "--seed_dir", "data/seed", "--processed_dir", "data/processed", "--out_cards", "action_cards"])

if __name__ == "__main__":
    main()
