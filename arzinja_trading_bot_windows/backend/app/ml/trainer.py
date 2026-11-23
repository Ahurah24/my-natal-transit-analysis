from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

from .features import FEATURE_COLUMNS, make_training_frame


class InsufficientTrainingData(ValueError):
    pass


def train_market_model(candles: pd.DataFrame, *, market: str, artifact_dir: str | Path,
                       horizon: int = 4, round_trip_fee_rate: float = 0.0,
                       estimated_round_trip_slippage: float = 0.001,
                       minimum_net_edge: float = 0.001) -> dict[str, Any]:
    """Train a per-market model with chronological 80/20 holdout, never random split."""
    dataset = make_training_frame(candles, horizon=horizon,
        round_trip_fee_rate=round_trip_fee_rate,
        estimated_round_trip_slippage=estimated_round_trip_slippage,
        minimum_net_edge=minimum_net_edge)
    if len(dataset) < 400:
        raise InsufficientTrainingData(f"{market}: need >=400 labeled rows; got {len(dataset)}")
    split = int(len(dataset) * 0.8)
    train, test = dataset.iloc[:split], dataset.iloc[split:]
    if train.target_win.nunique() < 2 or test.target_win.nunique() < 2:
        raise InsufficientTrainingData(f"{market}: both classes must exist in train and test windows")
    if min(train.target_win.value_counts().min(), test.target_win.value_counts().min()) < 20:
        raise InsufficientTrainingData(f"{market}: too few examples in one class")

    model = RandomForestClassifier(n_estimators=400, max_depth=7, min_samples_leaf=8,
        max_features="sqrt", class_weight="balanced_subsample", random_state=42, n_jobs=-1)
    model.fit(train[FEATURE_COLUMNS], train.target_win.astype(int))
    probabilities = model.predict_proba(test[FEATURE_COLUMNS])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    y_test = test.target_win.astype(int)
    metrics = {
        "market": market, "rows": int(len(dataset)), "train_rows": int(len(train)),
        "test_rows": int(len(test)), "test_win_rate": round(float(y_test.mean()), 4),
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "horizon_candles": horizon, "round_trip_fee_rate": round_trip_fee_rate,
        "estimated_round_trip_slippage": estimated_round_trip_slippage,
        "minimum_net_edge": minimum_net_edge,
        "warning": "Historical validation does not guarantee future performance."
    }
    output = Path(artifact_dir)
    output.mkdir(parents=True, exist_ok=True)
    safe_market = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in market)
    joblib.dump({"model": model, "features": FEATURE_COLUMNS, "market": market, "metrics": metrics},
                output / f"{safe_market}.joblib")
    (output / f"{safe_market}.metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def load_market_model(path: str | Path) -> dict[str, Any]:
    artifact = joblib.load(path)
    if not isinstance(artifact, dict) or "model" not in artifact or "features" not in artifact:
        raise ValueError("Invalid model artifact")
    return artifact
