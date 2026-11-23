from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .trainer import train_market_model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train one ML ranking model per OHLCV CSV market")
    parser.add_argument("--data-dir", default="data/historical")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--horizon", type=int, default=4)
    parser.add_argument("--fee", type=float, default=0.0, help="Round-trip fee rate as decimal")
    parser.add_argument("--slippage", type=float, default=0.001, help="Estimated round-trip slippage as decimal")
    parser.add_argument("--edge", type=float, default=0.001, help="Minimum net return to label a win")
    args = parser.parse_args()
    files = sorted(Path(args.data_dir).glob("*.csv"))
    if not files:
        raise SystemExit(f"No CSV files found in {Path(args.data_dir).resolve()}")
    for csv_path in files:
        market = csv_path.stem.upper()
        try:
            metrics = train_market_model(pd.read_csv(csv_path), market=market,
                artifact_dir=args.model_dir, horizon=args.horizon,
                round_trip_fee_rate=args.fee,
                estimated_round_trip_slippage=args.slippage,
                minimum_net_edge=args.edge)
            print(f"{market}: AUC={metrics['roc_auc']} precision={metrics['precision']} rows={metrics['rows']}")
        except ValueError as exc:
            print(f"SKIPPED {market}: {exc}")


if __name__ == "__main__":
    main()
