from datetime import date

import pytest

from btc_cycle.core.chart import build_overlays, nearest_zone, rally_from_low
from btc_cycle.core.planner import PlanInputs, Planner


@pytest.fixture
def plan(kb):
    inp = PlanInputs(capital=10000, btc_price_usd=64000, currency="USD", today=date(2026, 9, 26),
                     ma200=70000)
    return Planner(kb).build(inp)


def test_overlays(plan):
    ov = build_overlays(plan, date(2025, 9, 26), date(2027, 9, 26))
    kinds = {lv.kind for lv in ov.levels}
    assert "ladder" in kinds and "ma200" in kinds
    assert len([lv for lv in ov.levels if lv.kind == "ladder"]) == len(plan.ladder)
    assert {w.kind for w in ov.windows} == {"window", "bottom"}
    assert ov.floor_curve[0][0] == date(2025, 9, 26)
    assert all(f < v for (_, f), (_, v) in zip(ov.floor_curve, ov.fair_curve))


def test_nearest_zone(plan):
    _, dist = nearest_zone(plan, 64000)
    assert dist != 0  # prezzo fuori da tutte le zone
    z = plan.ladder[1]
    assert nearest_zone(plan, (z["low"] + z["high"]) / 2) == (2, 0.0)


def test_rally_from_low():
    assert rally_from_low([100, 200, 150, 100, 130], 130) == (100, pytest.approx(30))
    assert rally_from_low([1.0], 1.0) is None
