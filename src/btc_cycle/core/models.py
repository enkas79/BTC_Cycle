"""Strutture dati del dominio."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Insight:
    """Un'informazione strutturata estratta da un documento."""

    category: str  # es. "ciclo", "power_law", "ladder"
    key: str  # chiave del parametro di strategia, es. "cycle.peak_offset_months"
    value: Any  # valore serializzabile JSON
    label: str  # descrizione leggibile
    evidence: str = ""  # frammento di testo da cui deriva
    page: int = 0  # pagina (1-based)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Insight:
        return cls(**data)


@dataclass
class Document:
    """Documento importato con il testo e gli insight estratti."""

    doc_id: str
    filename: str
    title: str
    source: str
    doc_date: Optional[str]  # ISO yyyy-mm-dd
    imported_at: str
    pages: List[str]
    insights: List[Insight] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    extractor_version: int = 0
    meta_title: str = ""
    meta_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["insights"] = [i.to_dict() for i in self.insights]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Document:
        data = dict(data)
        data["insights"] = [Insight.from_dict(i) for i in data.get("insights", [])]
        return cls(**data)


@dataclass
class ParamValue:
    """Valore effettivo di un parametro, con la fonte e i valori alternativi."""

    key: str
    value: Any
    label: str
    doc_title: str
    doc_date: Optional[str]
    alternatives: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def has_conflict(self) -> bool:
        return any(a["value"] != self.value for a in self.alternatives)


@dataclass
class MarketSnapshot:
    """Dati di mercato scaricati (tutti opzionali)."""

    price_usd: Optional[float] = None
    usd_per_eur: Optional[float] = None
    ma200: Optional[float] = None
    high200: Optional[float] = None
    cycle_low_close: Optional[float] = None
    fear_greed: Optional[int] = None
    errors: List[str] = field(default_factory=list)
