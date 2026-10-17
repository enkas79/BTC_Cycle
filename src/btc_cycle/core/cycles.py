"""Sovrapposizione dei cicli: prezzo normalizzato al giorno dell'halving, in funzione dei giorni trascorsi."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Dict, List, Sequence, Tuple

from .cycle import HALVINGS


def _ts(d: date) -> float:
    return datetime.combine(d, time(), tzinfo=timezone.utc).timestamp()


def cycle_series(history: Sequence[Tuple[float, float]], halvings: Sequence[date] = HALVINGS,
                 days: int = 1500) -> Dict[date, List[Tuple[int, float]]]:
    """Per ogni halving: (giorni dall'halving, prezzo / prezzo all'halving), fino a ``days`` giorni.

    L'halving del 2012 è il primo con dati: i cicli precedenti non hanno storico.
    """
    out: Dict[date, List[Tuple[int, float]]] = {}
    for h in halvings:
        t0 = _ts(h)
        base = next((p for ts, p in history if ts >= t0), None)
        if base is None:
            continue
        rows = [(round((ts - t0) / 86400), p / base) for ts, p in history
                if t0 <= ts <= t0 + days * 86400]
        if len(rows) > 30:
            out[h] = rows
    return out
