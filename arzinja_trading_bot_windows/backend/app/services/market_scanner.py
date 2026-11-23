from __future__ import annotations

from typing import Any


def _truthy_flag(value: Any) -> bool:
    return value is True or value == 1 or str(value).lower() in {"1", "true", "yes"}


def eligible_zero_fee_markets(markets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Fail closed: only explicit zero-fee P2P markets with active buy/sell are returned."""
    output = []
    for market in markets:
        pair = market.get("pair")
        if not pair or not _truthy_flag(market.get("isZeroFee")):
            continue
        if not _truthy_flag(market.get("buyStatus")) or not _truthy_flag(market.get("sellStatus")):
            continue
        output.append(market)
    return output


def score_orderbook(pair: str, market: dict[str, Any], book: dict[str, Any]) -> dict[str, Any]:
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    if not bids or not asks:
        return {"pair": pair, "eligible": False, "reason": "empty orderbook"}
    best_bid, best_ask = float(bids[0][0]), float(asks[0][0])
    if best_bid <= 0 or best_ask <= 0 or best_ask < best_bid:
        return {"pair": pair, "eligible": False, "reason": "invalid or crossed orderbook"}
    mid = (best_bid + best_ask) / 2
    spread_pct = (best_ask - best_bid) / mid * 100
    bid_depth = sum(float(level[0]) * float(level[1]) for level in bids[:5])
    ask_depth = sum(float(level[0]) * float(level[1]) for level in asks[:5])
    depth = min(bid_depth, ask_depth)
    return {
        "pair": pair, "eligible": True, "is_zero_fee": True,
        "best_bid": best_bid, "best_ask": best_ask, "mid_price": mid,
        "spread_percent": round(spread_pct, 5),
        "top5_bid_quote_depth": round(bid_depth, 4),
        "top5_ask_quote_depth": round(ask_depth, 4),
        "min_notional": market.get("minNotional"),
        "max_notional": market.get("maxNotional"),
        "min_qty": market.get("minQty"), "max_qty": market.get("maxQty"),
        "base_precision": market.get("baseAssetPrecision"),
        "quote_precision": market.get("quotePrecision"),
        "liquidity_score": round(depth / (1 + spread_pct), 4),
    }


def scan_markets(client: Any, *, max_markets: int = 40, max_spread_percent: float = 0.8) -> list[dict[str, Any]]:
    markets = eligible_zero_fee_markets(client.all_p2p_markets())
    ranked = []
    for market in markets[:max_markets]:
        pair = str(market["pair"])
        book_response = client.orderbook(pair)
        book = book_response.get("result", {})
        result = score_orderbook(pair, market, book)
        if result.get("eligible") and result["spread_percent"] <= max_spread_percent:
            ranked.append(result)
    return sorted(ranked, key=lambda item: item["liquidity_score"], reverse=True)
