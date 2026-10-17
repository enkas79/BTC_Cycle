"""Fit della power law sullo storico: log10(prezzo) = a + b·log10(giorni dal genesis).

Il fair value è la retta di regressione; il floor è un percentile basso dei residui (di default il
2,5°), cioè il livello sotto il quale il prezzo è stato solo raramente. Il fit può essere calcolato
"as of" una data, usando solo i dati fino a quel giorno (nessun look-ahead: serve ai backtest).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import List, Optional, Sequence, Tuple

from .cycle import GENESIS, PowerLaw

START = date(2011, 1, 1)  # prima di allora il mercato è troppo sottile e il prezzo sotto 1 dollaro
MIN_POINTS = 365
DEFAULT_QUANTILE = 0.025


@dataclass
class PowerLawFit:
    exponent: float
    coeff: float
    floor_ratio: float
    r2: float
    n: int
    quantile: float

    def to_model(self) -> PowerLaw:
        return PowerLaw(coeff=self.coeff, exponent=self.exponent, floor_ratio=self.floor_ratio,
                        calibrated=True)


def _ts(d: date) -> float:
    return datetime.combine(d, time(), tzinfo=timezone.utc).timestamp()


def fit_power_law(history: Sequence[Tuple[float, float]], as_of: Optional[date] = None,
                  quantile: float = DEFAULT_QUANTILE) -> Optional[PowerLawFit]:
    lo, hi = _ts(START), _ts(as_of) + 86400 if as_of else float("inf")
    g = _ts(GENESIS)
    xs: List[float] = []
    ys: List[float] = []
    for ts, price in history:
        if lo <= ts < hi and price > 0:
            xs.append(math.log10(max(1, round((ts - g) / 86400))))
            ys.append(math.log10(price))
    n = len(xs)
    if n < MIN_POINTS:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    ss_tot = sum((y - my) ** 2 for y in ys)
    r2 = 1 - sum(r * r for r in resid) / ss_tot if ss_tot else 0.0
    floor = 10 ** sorted(resid)[int(quantile * (n - 1))]
    return PowerLawFit(exponent=b, coeff=10 ** a, floor_ratio=floor, r2=r2, n=n, quantile=quantile)
