from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "return_1", "return_3", "return_6", "return_12", "ema_gap", "ema_slope",
    "rsi_14", "macd_hist", "atr_pct", "bb_position", "bb_width", "volume_ratio",
    "realized_volatility", "candle_body_pct", "upper_wick_pct", "lower_wick_pct",
]
REQUIRED_COLUMNS = {"open", "high", "low", "close", "volume"}


def _rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return (100 - (100 / (1 + rs))).fillna(50)


def build_features(candles: pd.DataFrame, *, drop_last_candle: bool = True) -> pd.DataFrame:
    """Build causal OHLCV features. The final possibly-open candle is dropped by default."""
    missing = REQUIRED_COLUMNS.difference(candles.columns)
    if missing:
        raise ValueError(f"Missing OHLCV columns: {', '.join(sorted(missing))}")
    frame = candles.copy()
    for column in REQUIRED_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=list(REQUIRED_COLUMNS)).sort_index()
    if drop_last_candle and len(frame):
        frame = frame.iloc[:-1].copy()
    if len(frame) < 60:
        raise ValueError("At least 60 closed candles are required")

    close = frame["close"].replace(0, np.nan)
    high, low, volume = frame["high"], frame["low"], frame["volume"]
    ema_fast = close.ewm(span=12, adjust=False).mean()
    ema_slow = close.ewm(span=26, adjust=False).mean()
    ema_20 = close.ewm(span=20, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    previous_close = close.shift(1)
    true_range = pd.concat([(high-low), (high-previous_close).abs(), (low-previous_close).abs()], axis=1).max(axis=1)
    atr = true_range.ewm(alpha=1/14, adjust=False, min_periods=14).mean()
    middle = close.rolling(20).mean()
    std = close.rolling(20).std(ddof=0)
    upper, lower = middle + 2*std, middle - 2*std

    features = pd.DataFrame(index=frame.index)
    for period in (1, 3, 6, 12):
        features[f"return_{period}"] = close.pct_change(periods=period)
    features["ema_gap"] = ema_20 / ema_50 - 1
    features["ema_slope"] = ema_20.pct_change(5)
    features["rsi_14"] = _rsi(close) / 100.0
    features["macd_hist"] = (macd - macd_signal) / close
    features["atr_pct"] = atr / close
    features["bb_position"] = ((close-lower) / (upper-lower).replace(0, np.nan)).clip(-1, 2)
    features["bb_width"] = (upper-lower) / middle.replace(0, np.nan)
    features["volume_ratio"] = volume / volume.rolling(20).mean().replace(0, np.nan)
    features["realized_volatility"] = close.pct_change().rolling(20).std()
    candle_range = (high-low).replace(0, np.nan)
    features["candle_body_pct"] = (close-frame["open"]) / close
    features["upper_wick_pct"] = (high-pd.concat([frame["open"], close], axis=1).max(axis=1)) / close
    features["lower_wick_pct"] = (pd.concat([frame["open"], close], axis=1).min(axis=1)-low) / close
    return features.replace([np.inf, -np.inf], np.nan)


def make_training_frame(candles: pd.DataFrame, *, horizon: int = 4,
                        round_trip_fee_rate: float = 0.0,
                        estimated_round_trip_slippage: float = 0.001,
                        minimum_net_edge: float = 0.001) -> pd.DataFrame:
    """Label future returns after round-trip fees and estimated slippage."""
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    if min(round_trip_fee_rate, estimated_round_trip_slippage, minimum_net_edge) < 0:
        raise ValueError("costs and minimum_net_edge cannot be negative")
    feature_frame = build_features(candles, drop_last_candle=True)
    aligned = candles.loc[feature_frame.index]
    close = pd.to_numeric(aligned["close"], errors="coerce")
    future_close = close.shift(-horizon)
    net_return = future_close / close - 1 - round_trip_fee_rate - estimated_round_trip_slippage
    result = feature_frame.copy()
    result["forward_net_return"] = net_return
    result["target_win"] = (net_return > minimum_net_edge).astype(float)
    return result.dropna(subset=FEATURE_COLUMNS + ["forward_net_return"])
