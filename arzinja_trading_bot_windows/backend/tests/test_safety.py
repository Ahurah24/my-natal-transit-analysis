from app.services.market_scanner import eligible_active_p2p_markets
from app.services.risk import RiskManager


def test_active_p2p_filter_does_not_use_is_zero_fee():
    rows = [
        {"pair": "AAAIRT", "isZeroFee": 0, "buyStatus": 1, "sellStatus": 1},
        {"pair": "BBBIRT", "isZeroFee": 1, "buyStatus": 1, "sellStatus": 1},
        {"pair": "CCCIRT", "isZeroFee": 0, "buyStatus": 0, "sellStatus": 1},
        {"pair": "DDD", "buyStatus": 1, "sellStatus": 1},
    ]
    assert [x["pair"] for x in eligible_active_p2p_markets(rows)] == ["AAAIRT", "BBBIRT"]


def test_nested_market_wrapper_shape_is_flattened():
    wrapped = [{"BTCIRT": {"pair": "BTCIRT", "buyStatus": 1, "sellStatus": 1}},
               {"ETHIRT": {"pair": "ETHIRT", "buyStatus": 1, "sellStatus": 1}}]
    flattened = [value for item in wrapped for value in item.values()]
    assert [row["pair"] for row in flattened] == ["BTCIRT", "ETHIRT"]


def test_risk_manager_blocks_daily_loss_limit():
    risk = RiskManager()
    result = risk.size_position(equity=1000, entry_price=100, stop_price=98,
        available_quote=500, open_positions=0, trades_today=0, daily_pnl=-25)
    assert result["allowed"] is False


def test_risk_manager_caps_position_and_allows_small_risk():
    risk = RiskManager()
    result = risk.size_position(equity=1000, entry_price=100, stop_price=98,
        available_quote=500, open_positions=0, trades_today=0, daily_pnl=0)
    assert result["allowed"] is True
    assert result["notional"] <= 100
