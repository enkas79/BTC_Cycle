"""Dialoghi: guida in finestra e proposta di aggiornamento."""

from __future__ import annotations

from typing import Callable

from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

from .. import APP_NAME
from ..guide import CSS, guide_html
from ..i18n import get_lang, tr
from ..updater import ReleaseInfo


class HelpDialog(QDialog):
    """Guida in finestra: HTML con indice laterale e ricerca (finestra non modale)."""

    def __init__(self, on_pdf: Callable[[], None], parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("Guida — {app}").format(app=APP_NAME))
        self.resize(1100, 760)
        html, titles = guide_html(get_lang())
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(True)
        self.browser.document().setDefaultStyleSheet(CSS)
        self.browser.setHtml(html)
        toc = QListWidget()
        toc.setFixedWidth(310)
        toc.addItems(titles)
        toc.currentRowChanged.connect(lambda i: self.browser.scrollToAnchor(f"s{i + 1}"))
        self.search = QLineEdit()
        self.search.setPlaceholderText(tr("Cerca nella guida…"))
        self.search.setClearButtonEnabled(True)
        self.search.returnPressed.connect(self._find)
        pdf = QPushButton(tr("Apri PDF"))
        pdf.clicked.connect(on_pdf)

        side = QVBoxLayout()
        side.addWidget(self.search)
        side.addWidget(toc, 1)
        side.addWidget(pdf)
        row = QHBoxLayout(self)
        row.addLayout(side)
        row.addWidget(self.browser, 1)

    def _find(self) -> None:
        text = self.search.text()
        if text and not self.browser.find(text):  # a fine documento riparte dall'inizio
            self.browser.moveCursor(QTextCursor.MoveOperation.Start)
            self.browser.find(text)


def ask_update(parent, release: ReleaseInfo, local_version: str) -> bool:
    box = QMessageBox(parent)
    box.setIcon(QMessageBox.Icon.Information)
    box.setWindowTitle(tr("Aggiornamento disponibile"))
    box.setText(tr("È disponibile la versione {new} (installata: {old}).\n"
                   "Vuoi scaricarla e installarla ora?").format(new=release.version, old=local_version))
    if release.notes:
        box.setDetailedText(release.notes)
    box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    box.setDefaultButton(QMessageBox.StandardButton.Yes)
    return box.exec() == QMessageBox.StandardButton.Yes
