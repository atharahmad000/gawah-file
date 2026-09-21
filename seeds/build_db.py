"""Build a fresh demo database. Reset is explicit to protect review history."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from repos.db import ROOT, connect, data_path

SOURCES = ["schema.sql", "seed_wallets.sql", "seed_merchants.sql", "seed_transactions.sql", "seed_links_flags.sql", "seed_alerts_cases.sql", "seed_labels.sql", "seed_memories.sql"]


def build(reset=False, stage="all"):
    path = data_path()
    if path.exists() and path.stat().st_size:
        if not reset:
            raise FileExistsError("Database already exists. Use --reset only to discard this demo's operational history.")
        path.unlink()
    sources = SOURCES[:1] if stage == "schema" else SOURCES[:3] if stage == "identities" else SOURCES
    with connect() as conn:
        for name in sources:
            conn.executescript((ROOT / "seeds" / name).read_text(encoding="utf-8"))
        print("Tables:", ", ".join(r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")))
    if stage == "all" and (ROOT / "playbook/T01_first_credit_drain.md").exists():
        from seeds.seed_playbook_sql import seed_playbook
        seed_playbook()
    if stage == "all" and (ROOT / "risk/features_sql.py").exists():
        from risk.features_sql import rebuild
        rebuild()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--stage", choices=["schema", "identities", "all"], default="all")
    args = parser.parse_args()
    build(args.reset, args.stage)
