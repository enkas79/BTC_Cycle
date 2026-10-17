import json
import math
import time
from datetime import date

import pytest

from btc_cycle.core import history as hist
from btc_cycle.core.cycles import cycle_series
from btc_cycle.core.powerlaw_fit import _ts, fit_power_law


def synthetic(exponent=5.5, coeff=1e-16, start=date(2011, 1, 1), end=date(2024, 1, 1)):
    from btc_cycle.core.cycle import GENESIS
    rows = []
    n = (end - start).days
    for i in range(n):
        days = (start - GENESIS).days + i
        wobble = 1 + 0.2 * math.sin(i / 37.0)
        rows.append((_ts(start) + i * 86400, coeff * days ** exponent * wobble))
    return rows


def test_fit_recovers_exponent():
    fit = fit_power_law(synthetic())
    assert fit.exponent == pytest.approx(5.5, abs=0.05) and fit.r2 > 0.99
    assert 0.7 < fit.floor_ratio < 0.9  # percentile basso del rumore ±20%


def test_fit_is_point_in_time():
    h = synthetic()
    h = h + [(ts, 1e9) for ts, _ in h[-30:]]  # dati "futuri" assurdi dopo la data di riferimento
    early = fit_power_law(h, as_of=date(2023, 1, 1))
    assert early.exponent == pytest.approx(5.5, abs=0.05)  # non vede i valori anomali
    assert fit_power_law(h[:100]) is None  # storico insufficiente


def test_cycle_series_normalized():
    h = synthetic(start=date(2012, 1, 1), end=date(2016, 1, 1))
    out = cycle_series(h, halvings=[date(2012, 11, 28)], days=400)
    rows = out[date(2012, 11, 28)]
    assert rows[0] == (0, pytest.approx(1.0)) and rows[-1][0] <= 400


def test_load_history_cache(tmp_path, monkeypatch):
    path = tmp_path / "h.json"
    monkeypatch.setattr(hist, "fetch_full_history", lambda: [(1.0, 2.0)])
    assert hist.load_history(path) == [(1.0, 2.0)] and path.exists()
    monkeypatch.setattr(hist, "fetch_full_history", lambda: 1 / 0)
    assert hist.load_history(path) == [(1.0, 2.0)]  # cache fresca: nessun download
    old = time.time() - 48 * 3600
    import os
    os.utime(path, (old, old))
    assert json.loads(path.read_text()) and hist.load_history(path) == [(1.0, 2.0)]  # rete KO: cache scaduta
    path.unlink()
    with pytest.raises(ZeroDivisionError):
        hist.load_history(path)


def test_planner_uses_fit_and_warns(kb):
    from btc_cycle.core.planner import PlanInputs, Planner

    h = synthetic(end=date(2026, 9, 26))
    inp = dict(capital=10000, btc_price_usd=64000, currency="USD", today=date(2026, 9, 26))
    fit_plan = Planner(kb, history=h).build(PlanInputs(**inp))
    docs_plan = Planner(kb, history=h).build(PlanInputs(pl_mode="docs", **inp))
    assert fit_plan.situation["pl_source"] == "fit" and docs_plan.situation["pl_source"] == "docs"
    assert fit_plan.situation["floor"] != docs_plan.situation["floor"]
    assert any("fit" in w.lower() for w in fit_plan.warnings)
    assert Planner(kb).build(PlanInputs(**inp)).situation["pl_source"] == "docs"  # senza storico
