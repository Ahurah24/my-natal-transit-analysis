from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import StandardScaler

from app.ml.features import FEATURE_COLUMNS


class AdaptiveLearner:
    """Incremental, outcome-driven model. It only learns after a paper trade closes."""

    def __init__(self, artifact_path: str | Path = "models/adaptive_sgd.joblib"):
        self.artifact_path = Path(artifact_path)
        self.artifact_path.parent.mkdir(parents=True, exist_ok=True)
        self.scaler = StandardScaler()
        self.model = SGDClassifier(loss="log_loss", alpha=0.0005, random_state=42)
        self.is_fitted = False
        self.samples = 0
        self.classes = np.array([0, 1], dtype=int)
        if self.artifact_path.exists():
            artifact = joblib.load(self.artifact_path)
            self.scaler, self.model = artifact["scaler"], artifact["model"]
            self.samples, self.is_fitted = artifact["samples"], True

    def learn(self, features: dict[str, float], net_return_pct: float,
              minimum_edge_pct: float = 0.10) -> dict[str, Any]:
        if set(FEATURE_COLUMNS).difference(features):
            raise ValueError("Incomplete feature vector")
        x = pd.DataFrame([[float(features[name]) for name in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        if not np.isfinite(x.to_numpy()).all():
            raise ValueError("Feature vector contains non-finite values")
        label = int(net_return_pct > minimum_edge_pct)
        if not self.is_fitted:
            scaled = self.scaler.partial_fit(x).transform(x)
            self.model.partial_fit(scaled, np.array([label]), classes=self.classes)
            self.is_fitted = True
        else:
            scaled = self.scaler.partial_fit(x).transform(x)
            self.model.partial_fit(scaled, np.array([label]))
        self.samples += 1
        joblib.dump({"scaler": self.scaler, "model": self.model, "samples": self.samples,
                     "features": FEATURE_COLUMNS}, self.artifact_path)
        return {"learned": True, "label": label, "samples": self.samples,
                "note": "One closed paper-trade outcome was incorporated; not a live-trading authorization."}

    def predict(self, features: dict[str, float]) -> dict[str, Any]:
        if not self.is_fitted:
            return {"available": False, "reason": "model has no closed paper-trade outcomes yet"}
        x = pd.DataFrame([[float(features[name]) for name in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        probability = float(self.model.predict_proba(self.scaler.transform(x))[0, 1])
        return {"available": True, "probability_positive_net_return": probability,
                "samples": self.samples}
