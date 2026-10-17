"""Storico completo del prezzo BTC (chiusure giornaliere dal 2010), con cache su disco."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Tuple

from .market import _get_json

URL = "https://api.blockchain.info/charts/market-price?timespan=all&sampled=false&format=json"
MAX_AGE_H = 20  # il dato è giornaliero: oltre questa età si riscarica

History = List[Tuple[float, float]]  # (timestamp in secondi, prezzo USD)


def fetch_full_history() -> History:
    data = _get_json(URL)
    return [(float(v["x"]), float(v["y"])) for v in data["values"] if float(v["y"]) > 0]


def load_history(path: Path) -> History:
    """Cache fresca se c'è, altrimenti download; se la rete manca ripiega sulla cache scaduta."""
    cached: History = []
    if path.exists():
        try:
            cached = [tuple(r) for r in json.loads(path.read_text(encoding="utf-8"))]
        except (OSError, ValueError):
            cached = []
        if cached and time.time() - path.stat().st_mtime < MAX_AGE_H * 3600:
            return cached
    try:
        rows = fetch_full_history()
    except Exception:
        if cached:
            return cached
        raise
    path.write_text(json.dumps(rows), encoding="utf-8")
    return rows
