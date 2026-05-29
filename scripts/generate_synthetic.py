"""CLI wrapper for src.ingest.synthetic.generate."""

import argparse
from pathlib import Path

from src.ingest.synthetic import generate


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic transaction data.")
    parser.add_argument("--out-dir", type=Path, default=Path("data/synthetic"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--months", type=int, default=12)
    args = parser.parse_args()
    summary = generate(out_dir=args.out_dir, seed=args.seed, months=args.months)
    start, end = summary["date_range"]
    print(
        f"Generated {summary['rows']} rows | {start} → {end} | "
        f"accounts: {summary['accounts']} | anomalies: {summary['anomalies_injected']}"
    )


if __name__ == "__main__":
    main()
