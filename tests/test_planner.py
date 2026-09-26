from datetime import date

import pytest

from btc_cycle.core import cycle as cy
from btc_cycle.core.knowledge import KnowledgeBase
from btc_cycle.core.planner import PlanInputs, Planner
from btc_cycle.core.report import render_html, render_markdown


def inputs(**kw):
    base = dict(capital=10000, btc_price_usd=64000, currency="USD", today=date(2026, 9, 26))
    base.update(kw)
    return PlanInputs(**base)


def test_add_months_and_phase():
    assert cy.add_months(date(2024, 4, 20), 30) == date(2026, 10, 20)
    assert cy.add_months(date(2024, 1, 31), 1) == date(2024, 2, 29)
    m = cy.months_between(date(2024, 4, 20), date(2026, 9, 26))
    assert cy.cycle_phase(m, 18, 30, 48).key == "bottom"
    assert cy.cycle_phase(17.5, 18, 30, 48).key == "peak"


def test_power_law_calibration():
    pl = cy.PowerLaw()
    pl.calibrate_fair(64590, 43, date(2026, 7, 20))
    assert pl.fair_value(date(2026, 7, 20)) == pytest.approx(64590 / 0.57)
    pl.calibrate_floor(57500, date(2026, 7, 22))
    assert pl.floor(date(2026, 7, 22)) == pytest.approx(57500)


def test_plan_with_documents(kb):
    plan = Planner(kb).build(inputs(cycle_low_close=57735, fear_greed=20))
    assert plan.situation["phase"].key == "bottom"
    assert plan.pots["bottom"] == 5000 and plan.pots["dca"] == 5000
    # ladder: 50% del capitale del minimo + riserva flush sull'ultimo gradino
    assert sum(r["amount"] for r in plan.ladder) == pytest.approx(5000 * 0.5 + 500)
    assert plan.ladder[0]["trigger"] == 57735  # regola del nuovo minimo di chiusura
    assert plan.situation["ladder_factor"] > 1  # floor cresciuto da luglio
    assert sum(x["amount"] for x in plan.dca) == pytest.approx(5000)
    assert plan.boost_now["total"] == 25
    assert [s["date"] for s in plan.exit_steps][0] == date(2029, 4, 17)
    assert any("stessa fonte" in w for w in plan.warnings)
    assert any("Incoerenza" in w for w in plan.warnings)
    assert "Cosa fare adesso" in render_markdown(plan)
    assert "<table>" in render_html(plan)


def test_plan_without_documents_uses_defaults():
    plan = Planner(KnowledgeBase()).build(inputs())
    assert len(plan.ladder) == 4
    assert any("non calibrata" in w for w in plan.warnings)


def test_peak_phase_keeps_capital_idle(kb):
    plan = Planner(kb).build(inputs(today=date(2025, 10, 10), btc_price_usd=120000))
    assert plan.pots["idle"] == 10000 and not plan.ladder[0]["amount"]


def test_invalid_inputs(kb):
    with pytest.raises(ValueError):
        Planner(kb).build(inputs(btc_price_usd=0))


def test_kb_roundtrip_and_conflicts(kb):
    clone = KnowledgeBase.from_json(kb.to_json())
    assert clone.effective_params().keys() == kb.effective_params().keys()
    assert len(clone.sources()) == 1
