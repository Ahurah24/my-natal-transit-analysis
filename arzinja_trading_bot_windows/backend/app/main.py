from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.exchange.arzinja import ArzinjaClient, ArzinjaAPIError
from app.services.market_scanner import scan_markets, eligible_zero_fee_markets
from app.services.paper_ledger import PaperLedger

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

APP_NAME = "Arzinja Trading Bot - Windows"
TRADING_MODE = "paper"  # hard-locked until a separately reviewed live executor exists
LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"
ARM_LIVE_TRADING = os.getenv("ARM_LIVE_TRADING", "false").lower() == "true"

app = FastAPI(title=APP_NAME, version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_started_at = datetime.now(timezone.utc)
client = ArzinjaClient()
ledger = PaperLedger(ROOT / "backend" / "data" / "paper_trading.sqlite3")


def runtime_status() -> dict[str, Any]:
    return {
        "app": APP_NAME,
        "status": "ready",
        "mode": TRADING_MODE,
        "live_trading_enabled": False,
        "live_execution_supported": False,
        "exchange_credentials_configured": client.credentials_configured,
        "exchange_connected": False,
        "market_data": "not_connected",
        "strategy": "not_started",
        "paper_ledger": ledger.summary(),
        "started_at": _started_at.isoformat(),
        "server_time": datetime.now(timezone.utc).isoformat(),
        "notice": "اتصال فقط‌خواندنی قابل آزمایش است؛ اجرای سفارش واقعی عمداً در این نسخه فعال نشده است.",
    }


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/status")
def status() -> dict[str, Any]:
    return runtime_status()


@app.get("/api/config")
def public_config() -> dict[str, Any]:
    return {
        "default_mode": "paper",
        "live_trading_enabled": False,
        "supported_quote_currencies": ["IRT", "USDT"],
        "default_timeframe": "15m",
        "zero_fee_only": True,
        "advanced_trade_endpoint_only": True,
        "historical_candles_available_from_exchange_docs": False,
    }


@app.get("/api/exchange/markets")
def exchange_markets() -> dict[str, Any]:
    try:
        markets = client.all_p2p_markets()
        eligible = eligible_zero_fee_markets(markets)
        return {"total_p2p_markets": len(markets), "zero_fee_active_markets": len(eligible),
                "markets": eligible}
    except ArzinjaAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/exchange/scan")
def exchange_scan(max_markets: int = 40, max_spread_percent: float = 0.8) -> dict[str, Any]:
    if not 1 <= max_markets <= 100 or not 0 < max_spread_percent <= 5:
        raise HTTPException(status_code=422, detail="Invalid scanner limits")
    try:
        results = scan_markets(client, max_markets=max_markets,
                               max_spread_percent=max_spread_percent)
        return {"count": len(results), "results": results,
                "notice": "فقط بازارهای فعال P2P با پرچم صریح isZeroFee بررسی شده‌اند."}
    except ArzinjaAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/exchange/balances")
def exchange_balances() -> dict[str, Any]:
    if not client.credentials_configured:
        raise HTTPException(status_code=400, detail="کلیدهای API در فایل محلی .env تنظیم نشده‌اند.")
    try:
        return client.balances()
    except ArzinjaAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/paper/summary")
def paper_summary() -> dict[str, Any]:
    return ledger.summary()


@app.websocket("/ws/status")
async def status_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(runtime_status())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
