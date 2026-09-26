"""Percorsi di risorse, versione e cartella dati (indipendente da Qt)."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def resource_root() -> Path:
    """Radice delle risorse: cartella del bundle PyInstaller o root del progetto."""
    bundle = getattr(sys, "_MEIPASS", None)
    if bundle:
        return Path(bundle)
    return Path(__file__).resolve().parents[2]


def read_version() -> str:
    """Legge la versione corrente da version.txt (fallback 0.0.0)."""
    try:
        return (resource_root() / "version.txt").read_text(encoding="utf-8").strip() or "0.0.0"
    except OSError:
        return "0.0.0"


def data_dir() -> Path:
    """Cartella dati utente (knowledge base, download aggiornamenti)."""
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    path = base / "BTC_Cycle"
    path.mkdir(parents=True, exist_ok=True)
    return path


def knowledge_path() -> Path:
    return data_dir() / "knowledge.json"
