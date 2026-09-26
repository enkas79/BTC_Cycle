"""Download dei dati di mercato (CoinGecko, alternative.me). Da usare solo in un worker."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, List

from .models import MarketSnapshot

COINGECKO = "https://api.coingecko.com/api/v3"
FNG_URL = "https://api.alternative.me/fng/?limit=1"
TIMEOUT = 15


def _get_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "BTC-Cycle-Planner",
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def compute_indicators(closes: List[float], snap: MarketSnapshot) -> None:
    """MA200, massimo a 200 giorni e minimo di chiusura dopo il massimo dell'anno."""
    if len(closes) >= 200:
        last = closes[-200:]
        snap.ma200 = sum(last) / len(last)
        snap.high200 = max(last)
    if closes:
        peak_idx = max(range(len(closes)), key=closes.__getitem__)
        after = closes[peak_idx:]
        snap.cycle_low_close = min(after) if len(after) > 1 else None


def fetch_market() -> MarketSnapshot:
    snap = MarketSnapshot()
    try:
        data = _get_json(f"{COINGECKO}/simple/price?ids=bitcoin&vs_currencies=usd,eur")
        snap.price_usd = float(data["bitcoin"]["usd"])
        snap.usd_per_eur = snap.price_usd / float(data["bitcoin"]["eur"])
    except Exception as exc:
        snap.errors.append(f"prezzo: {exc}")
    try:
        data = _get_json(
            f"{COINGECKO}/coins/bitcoin/market_chart?vs_currency=usd&days=365&interval=daily"
        )
        compute_indicators([float(p[1]) for p in data.get("prices", [])], snap)
    except Exception as exc:
        snap.errors.append(f"storico: {exc}")
    try:
        data = _get_json(FNG_URL)
        snap.fear_greed = int(data["data"][0]["value"])
    except Exception as exc:
        snap.errors.append(f"fear & greed: {exc}")
    return snap
