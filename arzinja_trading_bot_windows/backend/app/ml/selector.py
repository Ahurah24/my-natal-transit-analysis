from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .features import FEATURE_COLUMNS, build_features
from .trainer import load_market_model


def score_market(candles: pd.DataFrame, model_artifact: dict[str, Any], *, market: str,
                 is_zero_fee: bool, market_is_active: bool,
                 minimum_probability: float = 0.62) -> dict[str, Any]:
    """Rank-only decision. It never creates or submits an exchange order."""
    if not 0.5 < minimum_probability < 1:
        raise ValueError("minimum_probability must be between 0.5 and 1")
    if not is_zero_fee:
        return {"market": market, "eligible": False, "reason": "zero-fee flag is not confirmed"}
    if not market_is_active:
        return {"market": market, "eligible": False, "reason": "market is inactive"}
    if model_artifact.get("market") != market:
        return {"market": market, "eligible": False, "reason": "model-market mismatch"}
    features = build_features(candles, drop_last_candle=True)
    latest = features.dropna(subset=FEATURE_COLUMNS).tail(1)
    if latest.empty:
        return {"market": market, "eligible": False, "reason": "not enough valid closed-candle data"}
    probability = float(model_artifact["model"].predict_proba(latest[FEATURE_COLUMNS])[0, 1])
    passed = probability >= minimum_probability
    return {"market": market, "eligible": passed,
        "win_probability_estimate": round(probability, 4),
        "minimum_probability": minimum_probability,
        "reason": "model threshold met" if passed else "model confidence below threshold",
        "action": "candidate_for_paper_review" if passed else "skip",
        "order_placement": "not_supported_by_ml_module"}


def rank_markets(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eligible = [item for item in candidates if item.get("eligible")]
    return sorted(eligible, key=lambda item: item.get("win_probability_estimate", 0), reverse=True)


def load_artifact_for_market(model_dir: str | Path, market: str) -> dict[str, Any]:
    safe_market = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in market)
    return load_market_model(Path(model_dir) / f"{safe_market}.joblib")
