from app.exchange.arzinja import ArzinjaClient, ArzinjaAPIError


def test_all_p2p_markets_flattens_actual_symbol_wrapper(monkeypatch):
    client = ArzinjaClient(base_url="https://example.invalid/api")
    payload = {
        "result": [
            {"BTCIRT": {"pair": "BTCIRT", "buyStatus": 1, "sellStatus": 1}},
            {"ETHIRT": {"pair": "ETHIRT", "buyStatus": 1, "sellStatus": 1}},
        ],
        "pagination": {"total": 2, "count": 2, "per_page": 100},
    }
    monkeypatch.setattr(client, "markets", lambda **kwargs: payload)
    rows = client.all_p2p_markets()
    assert [row["pair"] for row in rows] == ["BTCIRT", "ETHIRT"]


def test_history_rejects_unsupported_one_minute_resolution():
    client = ArzinjaClient(base_url="https://example.invalid/api")
    try:
        client.history(symbol="BTCIRT", resolution=1, start=1, end=2)
    except ValueError as exc:
        assert "5, 15 and 60" in str(exc)
    else:
        raise AssertionError("Unsupported resolution should be rejected")


def test_history_validates_equal_ohlcv_array_lengths(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"s": "ok", "t": [100, 200], "o": [10, 11],
                    "h": [12, 13], "l": [9, 10], "c": [11], "v": [1, 2]}

    class FakeSession:
        def get(self, *args, **kwargs):
            return FakeResponse()

    client = ArzinjaClient(base_url="https://example.invalid/api")
    monkeypatch.setattr(client, "session", FakeSession())
    try:
        client.history(symbol="BTCIRT", resolution=5, start=1, end=2)
    except ArzinjaAPIError as exc:
        assert "inconsistent lengths" in str(exc)
    else:
        raise AssertionError("Mismatched OHLCV arrays should be rejected")


def test_official_hmac_payload_get_matches_documented_order():
    payload = ArzinjaClient.signature_payload(
        "GET", "1730000000000", "sample-key", 5000,
        "pair=BTCIRT&limit=5", ""
    )
    assert payload == "1730000000000sample-key5000pair=BTCIRT&limit=5"


def test_official_hmac_payload_post_uses_body_not_query():
    payload = ArzinjaClient.signature_payload(
        "POST", "1730000000000", "sample-key", 5000,
        "ignored=query", '{"pair":"BTCIRT","type":"LIMIT"}'
    )
    assert payload == '1730000000000sample-key5000{"pair":"BTCIRT","type":"LIMIT"}'


def test_orderbook_endpoint_and_documented_result_shape(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "success": True, "result": {
                    "symbol": "BTCIRT",
                    "bids": [["100", "2.5"], ["99", "3"]],
                    "asks": [["101", "1.5"], ["102", "2"]],
                }
            }

    class FakeSession:
        def request(self, method, url, **kwargs):
            assert method == "GET"
            assert url.endswith("/v1/services/trade/p2p/orderbook")
            assert kwargs["params"] == {"pair": "BTCIRT", "limit": 5}
            return FakeResponse()

    client = ArzinjaClient(base_url="https://api-v2.arzinja.ir/api")
    monkeypatch.setattr(client, "session", FakeSession())
    response = client.orderbook("BTCIRT", limit=5)
    assert response["result"]["bids"][0] == ["100", "2.5"]
    assert response["result"]["asks"][0] == ["101", "1.5"]
