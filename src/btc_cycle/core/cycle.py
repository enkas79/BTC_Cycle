"""Modello del ciclo degli halving e della power law."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Optional

GENESIS = date(2009, 1, 3)
HALVINGS = [date(2012, 11, 28), date(2016, 7, 9), date(2020, 5, 11), date(2024, 4, 20)]
NEXT_HALVING_ESTIMATE = date(2028, 4, 17)  # stima per altezza di blocco 1.050.000

# Power law standard (Santostasi): prezzo = A * giorni_dal_genesis ^ B
DEFAULT_PL_EXPONENT = 5.82
DEFAULT_PL_COEFF = 1.0117e-17
DEFAULT_FLOOR_RATIO = 0.42  # banda inferiore / fair value


def add_months(d: date, months: float) -> date:
    """Somma mesi (anche frazionari) a una data."""
    whole = int(months)
    y, m = divmod(d.month - 1 + whole, 12)
    year, month = d.year + y, m + 1
    last_day = [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28, 31, 30, 31,
                30, 31, 31, 30, 31, 30, 31][month - 1]
    result = date(year, month, min(d.day, last_day))
    return result + timedelta(days=round((months - whole) * 30.44))


def months_between(a: date, b: date) -> float:
    return (b - a).days / 30.44


def halving_dates(next_halving: Optional[date] = None) -> List[date]:
    return HALVINGS + [next_halving or NEXT_HALVING_ESTIMATE]


def last_halving(today: date, next_halving: Optional[date] = None) -> date:
    past = [h for h in halving_dates(next_halving) if h <= today]
    return past[-1] if past else HALVINGS[0]


def next_halving_after(today: date, next_halving: Optional[date] = None) -> date:
    future = [h for h in halving_dates(next_halving) if h > today]
    return future[0] if future else add_months(halving_dates(next_halving)[-1], 48)


@dataclass
class Phase:
    key: str
    name: str
    description: str


def cycle_phase(months_since_halving: float, peak_offset: int, bottom_offset: int,
                accumulation_end: int) -> Phase:
    """Classifica la fase del ciclo in base ai mesi trascorsi dall'ultimo halving."""
    m = months_since_halving
    if m < peak_offset - 2:
        return Phase("bull", "Rialzo post-halving",
                     "Fase storicamente rialzista: mantenere, niente nuovi acquisti aggressivi.")
    if m < peak_offset + 3:
        return Phase("peak", "Finestra di picco",
                     "Zona temporale dei massimi storici di ciclo: applicare il piano di uscita.")
    if m < bottom_offset - 3:
        return Phase("bear", "Mercato ribassista",
                     "Distribuzione e calo: preservare il capitale, preparare i livelli di acquisto.")
    if m < bottom_offset + 4:
        return Phase("bottom", "Finestra di minimo",
                     "Zona temporale dei minimi di ciclo: ladder + drip + riserva.")
    if m < accumulation_end:
        return Phase("accumulation", "Accumulo",
                     "Dopo il minimo, prima dell'halving: DCA front-loaded con boost.")
    return Phase("pre_halving", "Pre-halving",
                 "Ciclo maturo: mantenere, prepararsi al rialzo post-halving.")


@dataclass
class PowerLaw:
    """Fair value = coeff * giorni^exponent; floor = fair * floor_ratio."""

    coeff: float = DEFAULT_PL_COEFF
    exponent: float = DEFAULT_PL_EXPONENT
    floor_ratio: float = DEFAULT_FLOOR_RATIO
    calibrated: bool = False

    @staticmethod
    def days(d: date) -> int:
        return max(1, (d - GENESIS).days)

    def fair_value(self, d: date) -> float:
        return self.coeff * self.days(d) ** self.exponent

    def floor(self, d: date) -> float:
        return self.fair_value(d) * self.floor_ratio

    def calibrate_fair(self, price: float, pct_below: float, d: date) -> None:
        """Ricava il coefficiente da 'prezzo X è Y% sotto il fair value alla data d'."""
        fair = price / (1 - pct_below / 100.0)
        self.coeff = fair / self.days(d) ** self.exponent
        self.calibrated = True

    def calibrate_floor(self, floor_price: float, d: date) -> None:
        self.floor_ratio = floor_price / self.fair_value(d)
        self.calibrated = True
