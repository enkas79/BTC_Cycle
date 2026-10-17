"""Generazione della guida in PDF (QTextDocument → QPrinter). Va eseguita in un worker, non nel thread GUI."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QMarginsF
from PyQt6.QtGui import QFont, QPageLayout, QPageSize, QPdfWriter, QTextDocument

from . import APP_NAME
from .guide_en import GUIDE_EN
from .guide_it import GUIDE_IT
from .paths import data_dir, read_version

CSS = """
body { font-family: Arial, Helvetica, sans-serif; color: #1f2430; }
h1 { font-size: 24pt; color: #b35900; margin-bottom: 0; }
h2 { font-size: 15pt; color: #1f2430; margin-top: 18px; border-bottom: 1px solid #f0a040; }
h3 { font-size: 11.5pt; color: #b35900; margin-top: 12px; margin-bottom: 2px; }
p, li { font-size: 10pt; }
.sub { font-size: 11pt; color: #6b7280; }
.note { background-color: #fff4e5; padding: 6px; }
.tip { background-color: #eef3fb; padding: 6px; }
table { border-collapse: collapse; }
th { background-color: #2b3040; color: #ffffff; padding: 4px; font-size: 9.5pt; }
td { padding: 4px; font-size: 9.5pt; }
"""


def guide_path(lang: str) -> Path:
    return data_dir() / f"guida_{lang}_{read_version()}.pdf"


def build_guide_pdf(lang: str) -> str:
    """Crea (se manca) il PDF della guida nella lingua indicata e ne restituisce il percorso."""
    path = guide_path(lang)
    if path.exists():
        return str(path)
    body = (GUIDE_EN if lang == "en" else GUIDE_IT).format(app=APP_NAME, version=read_version())
    doc = QTextDocument()
    doc.setDefaultFont(QFont("Arial", 10))
    doc.setDefaultStyleSheet(CSS)
    doc.setHtml(f"<html><body>{body}</body></html>".replace("<table>", '<table border="1" cellspacing="0" '
                                                            'cellpadding="4" width="100%">'))
    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Unit.Millimeter)
    writer.setTitle(f"{APP_NAME} — {'User guide' if lang == 'en' else 'Guida'}")
    doc.print(writer)
    return str(path)
