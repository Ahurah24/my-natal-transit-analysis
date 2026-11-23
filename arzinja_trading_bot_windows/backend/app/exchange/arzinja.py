from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from typing import Any
from urllib.parse import urlencode

import requests


class ArzinjaAPIError(RuntimeError):
    pass


class ArzinjaClient:
    """Arzinja API client implementing the documented X-ARZ HMAC headers."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 api_secret: str | None = None, timeout: int = 15):
        self.base_url = (base_url or os.getenv("ARZINJA_BASE_URL") or
                         "https://api-v2.arzinja.app/api").rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("ARZINJA_API_KEY", "")
        self.api_secret = api_secret if api_secret is not None else os.getenv("ARZINJA_API_SECRET", "")
        self.recv_window = int(os.getenv("ARZINJA_RECV_WINDOW_MS", "5000"))
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    @property
    def credentials_configured(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def _headers(self, method: str, query_string: str = "", body: str = "") -> dict[str, str]:
        if not self.credentials_configured:
            raise ArzinjaAPIError("API credentials are not configured")
        timestamp = str(int(time.time() * 1000))
        prepared = (timestamp + self.api_key + str(self.recv_window) + query_string
                    if method.upper() == "GET"
                    else timestamp + self.api_key + str(self.recv_window) + body)
        signature = hmac.new(self.api_secret.encode(), prepared.encode(), hashlib.sha256).hexdigest()
        return {
            "X-ARZ-API-KEY": self.api_key,
            "X-ARZ-SIGN": signature,
            "X-ARZ-TIMESTAMP": timestamp,
            "X-ARZ-RECV-WINDOW": str(self.recv_window),
        }

    def request(self, method: str, endpoint: str, *, params: dict[str, Any] | None = None,
                payload: dict[str, Any] | None = None, private: bool = False) -> dict[str, Any]:
        method = method.upper()
        params = params or {}
        query_string = urlencode(params)
        body = json.dumps(payload or {}, separators=(",", ":"), ensure_ascii=False) if method in {"POST", "PUT"} else ""
        headers = self._headers(method, query_string, body) if private else {}
        url = self.base_url + endpoint
        try:
            response = self.session.request(
                method, url, params=params or None,
                data=body if body else None, headers=headers, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise ArzinjaAPIError(f"Arzinja transport error: {exc}") from exc
        except ValueError as exc:
            raise ArzinjaAPIError("Arzinja returned a non-JSON response") from exc
        if not isinstance(data, dict) or data.get("success") is False:
            message = data.get("message", "Unknown API error") if isinstance(data, dict) else "Invalid API response"
            raise ArzinjaAPIError(str(message))
        if "result" not in data:
            raise ArzinjaAPIError("API response has no result field")
        return data

    def markets(self, page: int = 1, per_page: int = 100) -> dict[str, Any]:
        return self.request("GET", "/v1/services/market/all-market",
                            params={"page": page, "per_page": per_page, "provider_type": "p2p"})

    def all_p2p_markets(self, max_pages: int = 20) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for page in range(1, max_pages + 1):
            response = self.markets(page=page, per_page=100)
            result = response.get("result", [])
            if isinstance(result, dict):
                rows = list(result.values())
            elif isinstance(result, list):
                rows = []
                for item in result:
                    rows.extend(item.values() if isinstance(item, dict) else [])
            else:
                raise ArzinjaAPIError("Unexpected market-list format")
            items.extend(row for row in rows if isinstance(row, dict))
            pagination = response.get("pagination", {})
            total_pages = int(pagination.get("total_pages", page)) if isinstance(pagination, dict) else page
            if page >= total_pages or not rows:
                break
        return items

    def orderbook(self, pair: str, limit: int = 20) -> dict[str, Any]:
        return self.request("GET", "/v1/services/trade/p2p/orderbook",
                            params={"pair": pair, "limit": limit})

    def balances(self) -> dict[str, Any]:
        return self.request("GET", "/v1/services/wallet/balances", private=True)

    def advance_order(self, *, pair: str, side: str, quantity: str,
                      order_type: str = "LIMIT", user_price: float | None = None) -> dict[str, Any]:
        """The only order route in this client is documented Advance Trade (P2P)."""
        if side not in {"BUY", "SELL"} or order_type not in {"LIMIT", "MARKET"}:
            raise ValueError("Invalid side or order type")
        payload: dict[str, Any] = {"pair": pair, "type": order_type, "side": side, "qty": quantity}
        if user_price is not None:
            payload["user_price"] = user_price
        return self.request("POST", "/v1/services/trade/p2p/order", payload=payload, private=True)

    def cancel_advance_order(self, order_id: int) -> dict[str, Any]:
        return self.request("POST", "/v1/services/trade/p2p/cancel",
                            payload={"order_id": int(order_id)}, private=True)
