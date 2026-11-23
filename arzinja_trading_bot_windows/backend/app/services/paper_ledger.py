from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class PaperLedger:
    """Durable local ledger; it never calls exchange order endpoints."""

    def __init__(self, db_path: str | Path = "data/paper_trading.sqlite3"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS paper_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair TEXT NOT NULL, side TEXT NOT NULL, quantity REAL NOT NULL,
                entry_price REAL NOT NULL, exit_price REAL, stop_price REAL,
                target_price REAL, status TEXT NOT NULL DEFAULT 'OPEN',
                pnl REAL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                closed_at TEXT
            )""")
            db.execute("""CREATE TABLE IF NOT EXISTS learning_outcomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT, pair TEXT NOT NULL,
                features_json TEXT NOT NULL, net_return REAL NOT NULL,
                outcome INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )""")

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def open_trade(self, pair: str, side: str, quantity: float, entry_price: float,
                   stop_price: float, target_price: float) -> int:
        if side != "BUY" or min(quantity, entry_price, stop_price, target_price) <= 0:
            raise ValueError("Paper ledger supports validated positive BUY positions only")
        with self._connect() as db:
            cursor = db.execute(
                "INSERT INTO paper_trades(pair,side,quantity,entry_price,stop_price,target_price) VALUES(?,?,?,?,?,?)",
                (pair, side, quantity, entry_price, stop_price, target_price))
            return int(cursor.lastrowid)

    def close_trade(self, trade_id: int, exit_price: float, round_trip_cost_pct: float = 0.0) -> dict[str, Any]:
        if exit_price <= 0 or round_trip_cost_pct < 0:
            raise ValueError("Invalid exit price or costs")
        with self._connect() as db:
            row = db.execute("SELECT pair,quantity,entry_price,status FROM paper_trades WHERE id=?",
                             (trade_id,)).fetchone()
            if not row or row[3] != "OPEN":
                raise ValueError("Paper trade not found or already closed")
            pair, quantity, entry, _ = row
            gross = (exit_price - entry) * quantity
            net = gross - (entry * quantity * round_trip_cost_pct / 100)
            db.execute("UPDATE paper_trades SET exit_price=?,pnl=?,status='CLOSED',closed_at=CURRENT_TIMESTAMP WHERE id=?",
                       (exit_price, net, trade_id))
            return {"trade_id": trade_id, "pair": pair, "gross_pnl": gross, "net_pnl": net}

    def open_positions(self) -> int:
        with self._connect() as db:
            return int(db.execute("SELECT COUNT(*) FROM paper_trades WHERE status='OPEN'").fetchone()[0])

    def summary(self) -> dict[str, Any]:
        with self._connect() as db:
            row = db.execute("""SELECT COUNT(*), SUM(CASE WHEN status='OPEN' THEN 1 ELSE 0 END),
                COALESCE(SUM(CASE WHEN status='CLOSED' THEN pnl ELSE 0 END),0)
                FROM paper_trades""").fetchone()
            return {"total_trades": row[0], "open_positions": row[1], "realized_net_pnl": row[2]}
