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
    """Arzinja API client. Order methods are restricted to Advance Trade (P2P)."""

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 api_secret: str | None = None, timeout: int = 15):
        self.base_url = (base_url or os.getenv("ARZINJA_BASE_URL") or
                         "https://api-v2.arzinja.ir/api").rstrip("/")
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
        try:
            response = self.session.request(
                method, self.base_url + endpoint, params=params or None,
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
        # Verified by the user's live PowerShell test on api-v2.arzinja.ir.
        return self.request("GET", "/v1/market/all-market",
                            params={"page": page, "per_page": per_page, "provider_type": "p2p"})

    def all_p2p_markets(self, max_pages: int = 20) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        per_page = 100
        for page in range(1, max_pages + 1):
            response = self.markets(page=page, per_page=per_page)
            result = response.get("result", [])
            if isinstance(result, dict):
                rows = list(result.values())
            elif isinstance(result, list):
                rows = []
                # Actual API shape: each array element is { "SYMBOL": { market fields } }.
                for item in result:
                    if isinstance(item, dict):
                        rows.extend(item.values())
            else:
                raise ArzinjaAPIError("Unexpected market-list format")
            rows = [row for row in rows if isinstance(row, dict)]
            items.extend(rows)
            pagination = response.get("pagination", {})
            total = pagination.get("total") if isinstance(pagination, dict) else None
            if not rows or len(rows) < per_page or (total is not None and len(items) >= int(total)):
                break
        return items

    def history(self, *, symbol: str, resolution: int, start: int, end: int,
                countback: int = 1000, currency_code: str = "IRT") -> dict[str, Any]:
        if resolution not in {5, 15, 60}:
            raise ValueError("Supported Arzinja candle resolutions are 5, 15 and 60 minutes")
        params = {
            "symbol": symbol, "resolution": resolution, "from": start, "to": end,
            "countback": countback, "currencyCode": currency_code,
        }
        try:
            response = self.session.get(
                self.base_url + "/v1/trade/trading-view/history",
                params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise ArzinjaAPIError(f"Arzinja history transport error: {exc}") from exc
        except ValueError as exc:
            raise ArzinjaAPIError("Arzinja history returned non-JSON data") from exc
        if not isinstance(data, dict) or data.get("s") != "ok":
            message = data.get("errmsg", "History request failed") if isinstance(data, dict) else "Invalid history response"
            raise ArzinjaAPIError(str(message))
        required = ("t", "o", "h", "l", "c", "v")
        if any(not isinstance(data.get(key), list) for key in required):
            raise ArzinjaAPIError("History response is missing OHLCV arrays")
        lengths = {len(data[key]) for key in required}
        if len(lengths) != 1:
            raise ArzinjaAPIError("History OHLCV arrays have inconsistent lengths")
        return data

    def orderbook(self, pair: str, limit: int = 20) -> dict[str, Any]:
        # This route still needs a live response-shape check against the user's account.
        return self.request("GET", "/v1/services/trade/p2p/orderbook",
                            params={"pair": pair, "limit": limit})

    def balances(self) -> dict[str, Any]:
        return self.request("GET", "/v1/services/wallet/balances", private=True)

    def advance_order(self, *, pair: str, side: str, quantity: str,
                      order_type: str = "LIMIT", user_price: float | None = None) -> dict[str, Any]:
        """Order route is Advance Trade (P2P) only; not used by the current app."""
        if side not in {"BUY", "SELL"} or order_type not in {"LIMIT", "MARKET"}:
            raise ValueError("Invalid side or order type")
        payload: dict[str, Any] = {"pair": pair, "type": order_type, "side": side, "qty": quantity}
        if user_price is not None:
            payload["user_price"] = user_price
        return self.request("POST", "/v1/services/trade/p2p/order", payload=payload, private=True)

    def cancel_advance_order(self, order_id: int) -> dict[str, Any]:
        return self.request("POST", "/v1/services/trade/p2p/cancel",
                            payload={"order_id": int(order_id)}, private=True)
