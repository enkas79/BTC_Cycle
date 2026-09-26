"""Lettura dei documenti sorgente (PDF, TXT, MD)."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

SUPPORTED_EXTENSIONS = (".pdf", ".txt", ".md")


@dataclass
class RawDocument:
    path: Path
    doc_id: str
    pages: List[str]
    meta_title: str = ""
    meta_date: Optional[str] = None


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()[:16]


def read_document(path: Path) -> RawDocument:
    """Estrae il testo per pagina. Solleva ValueError se il formato non è supportato."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Formato non supportato: {path.name}")
    doc_id = file_hash(path)
    if suffix == ".pdf":
        return _read_pdf(path, doc_id)
    text = path.read_text(encoding="utf-8", errors="replace")
    # Nei file di testo il form feed separa le pagine, se presente
    pages = [p for p in text.split("\f")] or [text]
    return RawDocument(path=path, doc_id=doc_id, pages=pages)


def _read_pdf(path: Path, doc_id: str) -> RawDocument:
    from pypdf import PdfReader  # import locale: pypdf è lento da caricare

    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        try:
            pages.append(page.extract_text() or "")
        except Exception:  # pagina corrotta: non blocca l'intero documento
            pages.append("")
    meta_title, meta_date = "", None
    meta = reader.metadata
    if meta is not None:
        meta_title = (meta.title or "").strip()
        try:
            created = meta.creation_date
        except Exception:
            created = None
        if created is not None:
            meta_date = created.date().isoformat()
    if not any(p.strip() for p in pages):
        raise ValueError(
            f"Nessun testo estraibile da {path.name} (PDF scansionato? serve OCR)."
        )
    return RawDocument(path, doc_id, pages, meta_title, meta_date)
