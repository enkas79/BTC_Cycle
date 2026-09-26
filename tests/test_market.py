from btc_cycle.core.market import compute_indicators
from btc_cycle.core.models import MarketSnapshot


def test_indicators():
    closes = [100.0] * 150 + [200.0] + [150.0, 120.0, 130.0] + [140.0] * 60
    snap = MarketSnapshot()
    compute_indicators(closes, snap)
    assert snap.high200 == 200.0
    assert snap.cycle_low_close == 120.0
    assert snap.ma200 is not None
