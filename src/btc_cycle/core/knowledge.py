"""Knowledge base: documenti analizzati e parametri di strategia aggregati."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import extractors as ex
from .models import Document, ParamValue
from .pdf_reader import SUPPORTED_EXTENSIONS, RawDocument, read_document

# Chiavi che rappresentano stime del minimo di ciclo (per il confronto tra fonti)
BOTTOM_KEYS = ("cycle.bottom_range", "cycle.bottom_scenarios", "power_law.floor",
               "levels.invalidation_down", "accum.ladder")


def build_document(raw: RawDocument, filename: Optional[str] = None) -> Document:
    """Analizza un documento grezzo e restituisce un Document completo."""
    name = filename or raw.path.name
    corpus, ctx, insights = ex.analyze_pages(raw.pages, raw.meta_date)
    source, _ = ex.detect_source(corpus)
    return Document(
        doc_id=raw.doc_id,
        filename=name,
        title=ex.detect_title(name, raw.meta_title),
        source=source,
        doc_date=ctx["doc_date"],
        imported_at=datetime.now().isoformat(timespec="seconds"),
        pages=raw.pages,
        insights=insights,
        flags=ex.detect_flags(corpus, raw.meta_title),
        extractor_version=ex.EXTRACTOR_VERSION,
        meta_title=raw.meta_title,
        meta_date=raw.meta_date,
    )


def reanalyze(doc: Document) -> Document:
    raw = RawDocument(Path(doc.filename), doc.doc_id, doc.pages, doc.meta_title, doc.meta_date)
    fresh = build_document(raw, doc.filename)
    fresh.imported_at = doc.imported_at
    return fresh


def source_key(doc: Document) -> str:
    key = doc.source.lstrip("@").lower()
    for tld in (".com", ".vip", ".io", ".net", ".org", ".co"):
        key = key[: -len(tld)] if key.endswith(tld) else key
    return "".join(ch for ch in key if ch.isalnum())


class KnowledgeBase:
    """Insieme di documenti; nessuna dipendenza da Qt, nessun I/O implicito."""

    def __init__(self, documents: Optional[List[Document]] = None):
        self.documents: Dict[str, Document] = {d.doc_id: d for d in documents or []}

    # --- persistenza (chiamata dai worker in background) ---
    def to_json(self) -> str:
        payload = {"version": 1, "documents": [d.to_dict() for d in self.documents.values()]}
        return json.dumps(payload, ensure_ascii=False, indent=1)

    @classmethod
    def from_json(cls, text: str) -> KnowledgeBase:
        data = json.loads(text)
        kb = cls([Document.from_dict(d) for d in data.get("documents", [])])
        kb.upgrade()
        return kb

    @classmethod
    def load(cls, path: Path) -> KnowledgeBase:
        if not Path(path).exists():
            return cls()
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    @staticmethod
    def save_text(path: Path, text: str) -> None:
        path = Path(path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def upgrade(self) -> int:
        """Rianalizza i documenti estratti con una versione precedente degli estrattori."""
        stale = [d for d in self.documents.values() if d.extractor_version < ex.EXTRACTOR_VERSION]
        for doc in stale:
            self.documents[doc.doc_id] = reanalyze(doc)
        return len(stale)

    def reanalyze_all(self) -> None:
        for doc_id, doc in list(self.documents.items()):
            self.documents[doc_id] = reanalyze(doc)

    # --- gestione documenti ---
    def add(self, doc: Document) -> bool:
        """Aggiunge o sostituisce. Restituisce False se era già presente."""
        is_new = doc.doc_id not in self.documents
        self.documents[doc.doc_id] = doc
        return is_new

    def remove(self, doc_id: str) -> None:
        self.documents.pop(doc_id, None)

    @staticmethod
    def effective_date(doc: Document) -> str:
        return doc.doc_date or doc.imported_at[:10]

    def sorted_documents(self) -> List[Document]:
        """Dal più recente al più vecchio."""
        return sorted(self.documents.values(), key=self.effective_date, reverse=True)

    # --- aggregazione ---
    def effective_params(self) -> Dict[str, ParamValue]:
        """Per ogni chiave vince il documento più recente; gli altri valori restano come alternative."""
        params: Dict[str, ParamValue] = {}
        for doc in self.sorted_documents():
            for ins in doc.insights:
                if ins.key.startswith(("level.", "error.")):
                    continue
                entry = {"value": ins.value, "doc_title": doc.title,
                         "doc_date": self.effective_date(doc)}
                if ins.key not in params:
                    params[ins.key] = ParamValue(ins.key, ins.value, ins.label, doc.title,
                                                 self.effective_date(doc))
                else:
                    params[ins.key].alternatives.append(entry)
        return params

    def value(self, key: str, default=None):
        param = self.effective_params().get(key)
        return param.value if param else default

    def bottom_estimates(self) -> List[Dict]:
        """Stime del minimo di ciclo per documento, normalizzate in un range [low, high]."""
        out = []
        for doc in self.sorted_documents():
            for ins in doc.insights:
                if ins.key not in BOTTOM_KEYS:
                    continue
                v = ins.value
                if ins.key == "cycle.bottom_range":
                    low, high = v["low"], v["high"]
                elif ins.key == "cycle.bottom_scenarios":
                    prices = [s["price"] for s in v]
                    low, high = min(prices), max(prices)
                elif ins.key == "power_law.floor":
                    low, high = v["low"], v["high"]
                elif ins.key == "levels.invalidation_down":
                    low = high = v["price"]
                else:  # ladder: dalla zona più profonda a quella più alta
                    low = min((z["high"] if z["low"] == 0 else z["low"]) for z in v)
                    high = max(z["high"] for z in v)
                out.append({"doc_title": doc.title, "key": ins.key, "label": ins.label,
                            "low": float(low), "high": float(high)})
        return out

    def sources(self) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        for doc in self.sorted_documents():
            groups.setdefault(source_key(doc) or doc.source, []).append(doc.title)
        return groups


# --- funzioni pensate per l'esecuzione in un worker ---


def import_files(paths: List[str], progress=None) -> Tuple[List[Document], List[str]]:
    """Legge e analizza i file; restituisce (documenti, errori) senza toccare la KB."""
    docs, errors = [], []
    files = collect_files(paths)
    for n, path in enumerate(files, start=1):
        if progress:
            progress(int((n - 1) * 100 / max(1, len(files))), path.name)
        try:
            docs.append(build_document(read_document(path)))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    if progress:
        progress(100, "")
    return docs, errors


def collect_files(paths: List[str]) -> List[Path]:
    """Espande le cartelle nei file supportati."""
    out: List[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            out += sorted(f for f in p.rglob("*") if f.suffix.lower() in SUPPORTED_EXTENSIONS)
        elif p.suffix.lower() in SUPPORTED_EXTENSIONS:
            out.append(p)
    return out


def reanalyzed_copy(text: str) -> KnowledgeBase:
    kb = KnowledgeBase.from_json(text)
    kb.reanalyze_all()
    return kb
