from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskConfig:
    risk_per_trade_pct: float = 0.005
    max_daily_loss_pct: float = 0.02
    max_position_pct: float = 0.10
    max_open_positions: int = 2
    max_trades_per_day: int = 8
    min_stop_distance_pct: float = 0.003


class RiskManager:
    def __init__(self, config: RiskConfig | None = None):
        self.config = config or RiskConfig()

    def size_position(self, *, equity: float, entry_price: float, stop_price: float,
                      available_quote: float, open_positions: int, trades_today: int,
                      daily_pnl: float) -> dict:
        if min(equity, entry_price, stop_price, available_quote) <= 0:
            return {"allowed": False, "reason": "non-positive equity, price or available balance"}
        if stop_price >= entry_price:
            return {"allowed": False, "reason": "long-position stop must be below entry"}
        if open_positions >= self.config.max_open_positions:
            return {"allowed": False, "reason": "maximum concurrent positions reached"}
        if trades_today >= self.config.max_trades_per_day:
            return {"allowed": False, "reason": "daily trade limit reached"}
        if daily_pnl <= -(equity * self.config.max_daily_loss_pct):
            return {"allowed": False, "reason": "daily loss limit reached"}
        stop_distance = (entry_price - stop_price) / entry_price
        if stop_distance < self.config.min_stop_distance_pct:
            return {"allowed": False, "reason": "stop distance is too small"}
        risk_budget = equity * self.config.risk_per_trade_pct
        qty_by_risk = risk_budget / (entry_price - stop_price)
        qty_by_exposure = (equity * self.config.max_position_pct) / entry_price
        qty_by_cash = available_quote / entry_price
        quantity = min(qty_by_risk, qty_by_exposure, qty_by_cash)
        if quantity <= 0:
            return {"allowed": False, "reason": "calculated quantity is zero"}
        return {
            "allowed": True, "quantity": quantity, "risk_budget": risk_budget,
            "stop_distance_pct": stop_distance * 100,
            "notional": quantity * entry_price,
            "risk_pct": self.config.risk_per_trade_pct * 100,
        }
