from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

APP_NAME = "Arzinja Trading Bot - Windows"
PAPER_TRADING = os.getenv("TRADING_MODE", "paper").lower() != "live"
LIVE_TRADING_ENABLED = os.getenv("LIVE_TRADING_ENABLED", "false").lower() == "true"

app = FastAPI(title=APP_NAME, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_started_at = datetime.now(timezone.utc)


def runtime_status() -> dict[str, Any]:
    return {
        "app": APP_NAME,
        "status": "ready",
        "mode": "paper" if PAPER_TRADING else "live",
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "exchange_connected": False,
        "market_data": "not_connected",
        "strategy": "not_started",
        "started_at": _started_at.isoformat(),
        "server_time": datetime.now(timezone.utc).isoformat(),
        "notice": "اتصال صرافی هنوز پیکربندی و اعتبارسنجی نشده است؛ هیچ داده یا موجودی ساختگی نمایش داده نمی‌شود.",
    }


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/status")
async def status() -> dict[str, Any]:
    return runtime_status()


@app.get("/api/config")
async def public_config() -> dict[str, Any]:
    # Never return API credentials or other secrets to the browser.
    return {
        "default_mode": "paper",
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "supported_quote_currencies": ["IRT", "USDT"],
        "default_timeframe": "15m",
        "fees_configured": bool(os.getenv("TRADING_FEE_RATE")),
    }


@app.websocket("/ws/status")
async def status_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(runtime_status())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        return
