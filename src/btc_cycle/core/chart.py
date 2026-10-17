"""Dati del grafico: livelli e finestre della strategia ricavati dal piano (nessuna GUI)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Sequence, Tuple

from ..i18n import tr
from .planner import Plan

# Rally falliti dei bear market dal 2011: picco mediano sopra il minimo (15 casi).
# Fonte: "The Pullback Playbook" (Bitcoin Daily). Campione ridotto: solo contesto.
FAILED_RALLY_MEDIAN_PCT = 35.0


@dataclass
class HLevel:
    """Livello orizzontale: linea (low == high) o fascia di prezzo."""

    label: str
    low: float
    high: float
    kind: str  # ladder | floor | fair | rialzo | ribasso | ma200


@dataclass
class VWindow:
    """Finestra temporale verticale (start == end: marcatore singolo)."""

    label: str
    start: date
    end: date
    kind: str  # window | bottom


@dataclass
class ChartOverlays:
    levels: List[HLevel] = field(default_factory=list)
    windows: List[VWindow] = field(default_factory=list)
    fair_curve: List[Tuple[date, float]] = field(default_factory=list)
    floor_curve: List[Tuple[date, float]] = field(default_factory=list)


def _k(v: float) -> str:
    return f"${v / 1000:,.0f}k"


def build_overlays(plan: Plan, start: date, end: date, step_days: int = 7) -> ChartOverlays:
    s, inp = plan.situation, plan.inputs
    out = ChartOverlays()
    for r in plan.ladder:
        rng = f"< {_k(r['high'])}" if r["low"] <= 0 else f"{_k(r['low'])}–{_k(r['high'])}"
        out.levels.append(HLevel(tr("Ladder {n} · {rng} · {pct}%").format(n=r["rung"], rng=rng, pct=r["pct"]),
                                 r["low"], r["high"], "ladder"))
    for lv in plan.levels:
        out.levels.append(HLevel(f"{lv['name']} · {_k(lv['price'])}", lv["price"], lv["price"],
                                 lv["kind"]))
    if inp.ma200:
        out.levels.append(HLevel(f"MA200 · {_k(inp.ma200)}", inp.ma200, inp.ma200, "ma200"))
    if s.get("window_start") and s.get("window_end"):
        out.windows.append(VWindow(tr("Finestra di minimo"), s["window_start"], s["window_end"], "window"))
    if s.get("est_bottom"):
        out.windows.append(VWindow(tr("Minimo stimato"), s["est_bottom"], s["est_bottom"], "bottom"))
    pl = s.get("power_law")
    if pl:
        d = start
        while d <= end:
            out.fair_curve.append((d, pl.fair_value(d)))
            out.floor_curve.append((d, pl.floor(d)))
            d += timedelta(days=step_days)
    return out


def nearest_zone(plan: Plan, price: float) -> Optional[Tuple[int, float]]:
    """Gradino di ladder più vicino al prezzo e distanza % (0 = prezzo dentro la zona)."""
    best: Optional[Tuple[int, float]] = None
    for r in plan.ladder:
        lo, hi = r["low"], r["high"]
        dist = 0.0 if lo <= price <= hi else ((hi if price > hi else lo) / price - 1) * 100
        if best is None or abs(dist) < abs(best[1]):
            best = (r["rung"], dist)
    return best


def rally_from_low(closes: Sequence[float], price: float) -> Optional[Tuple[float, float]]:
    """(minimo, rally %) dal minimo di chiusura successivo al massimo della serie."""
    if len(closes) < 2:
        return None
    peak = max(range(len(closes)), key=closes.__getitem__)
    low = min(closes[peak:])
    return (low, (price / low - 1) * 100) if low > 0 else None
