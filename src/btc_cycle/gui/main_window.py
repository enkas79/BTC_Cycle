"""Finestra principale: documenti, parametri, piano; menu e aggiornamenti."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Callable, List, Optional

from PyQt6.QtCore import QDate, QSettings, Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QDesktopServices, QKeySequence
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .. import APP_AUTHOR, APP_NAME, GITHUB_REPO, updater
from ..core.knowledge import KnowledgeBase, import_files, reanalyzed_copy
from ..core.market import fetch_market
from ..core.models import MarketSnapshot
from ..core.planner import PROFILES, PlanInputs, Planner
from ..core.report import render_html, render_markdown
from ..paths import data_dir, knowledge_path, read_version
from .dialogs import HelpDialog, ask_update
from .workers import TaskWorker

FILE_FILTER = "Documenti (*.pdf *.txt *.md);;PDF (*.pdf);;Tutti i file (*)"


def _item(text, align_right: bool = False) -> QTableWidgetItem:
    item = QTableWidgetItem(str(text))
    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    if align_right:
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return item


def _fmt(value) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, float):
        return f"{value:,.2f}".rstrip("0").rstrip(".")
    return str(value)


def _table(headers: List[str]) -> QTableWidget:
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setStretchLastSection(True)
    table.setWordWrap(False)
    return table


def _fit(table: QTableWidget, max_width: int = 380) -> None:
    """Adatta le colonne al contenuto con un limite (il testo completo è nel tooltip)."""
    table.resizeColumnsToContents()
    for col in range(table.columnCount() - 1):
        table.setColumnWidth(col, min(table.columnWidth(col), max_width))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.version = read_version()
        self.kb = KnowledgeBase()
        self.plan = None
        self._workers: set = set()
        self._update_busy = False
        self.settings = QSettings("enkas79", "BTC_Cycle")

        self.setWindowTitle(f"{APP_NAME} {self.version}")
        self.resize(1280, 820)
        self.setAcceptDrops(True)
        self._build_menu()
        self._build_ui()
        self._load_settings()
        self.statusBar().showMessage("Caricamento knowledge base…")

        self._run(KnowledgeBase.load, knowledge_path(), ok=self._on_kb_loaded,
                  fail=lambda e: self._on_kb_loaded(KnowledgeBase(), e))
        QTimer.singleShot(3000, lambda: self.check_updates(manual=False))

    # ------------------------------------------------------------------ worker
    def _run(self, fn: Callable, *args, ok: Callable, fail: Optional[Callable] = None,
             progress: Optional[Callable] = None) -> TaskWorker:
        worker = TaskWorker(fn, *args, with_progress=progress is not None, parent=self)
        worker.succeeded.connect(ok)
        worker.failed.connect(fail or (lambda e: self.statusBar().showMessage(f"Errore: {e}")))
        if progress:
            worker.progress.connect(progress)
        worker.finished.connect(lambda: self._workers.discard(worker))
        self._workers.add(worker)
        worker.start()
        return worker

    def _save_kb(self) -> None:
        text = self.kb.to_json()
        self._run(KnowledgeBase.save_text, knowledge_path(), text, ok=lambda _: None,
                  fail=lambda e: QMessageBox.warning(self, "Salvataggio", f"Impossibile salvare: {e}"))

    # -------------------------------------------------------------------- menu
    def _action(self, menu, text: str, slot: Callable, shortcut=None) -> QAction:
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(slot)
        menu.addAction(action)
        return action

    def _build_menu(self) -> None:
        bar = self.menuBar()
        m = bar.addMenu("&File")
        self._action(m, "Importa documenti…", self.import_dialog, QKeySequence.StandardKey.Open)
        self._action(m, "Importa cartella…", self.import_folder_dialog)
        m.addSeparator()
        self._action(m, "Esporta piano (HTML)…", lambda: self.export_plan("html"))
        self._action(m, "Esporta piano (Markdown)…", lambda: self.export_plan("md"))
        m.addSeparator()
        self._action(m, "Esci", self.close, QKeySequence.StandardKey.Quit)

        m = bar.addMenu("&Dati")
        self._action(m, "Aggiorna dati di mercato", self.refresh_market, "F5")
        self._action(m, "Genera piano", self.generate_plan, "Ctrl+G")
        self._action(m, "Rianalizza tutti i documenti", self.reanalyze_all)
        self._action(m, "Rimuovi documento selezionato", self.remove_selected)
        self._action(m, "Apri cartella dati", lambda: QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(data_dir()))))

        m = bar.addMenu("&Aiuto")
        self._action(m, "Guida", lambda: HelpDialog(self).exec(), "F1")
        self._action(m, "Controlla aggiornamenti", lambda: self.check_updates(manual=True))
        m.addSeparator()
        self._action(m, "Informazioni", self.show_about)

    # ---------------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_plan_tab(), "Piano")
        self.tabs.addTab(self._build_docs_tab(), "Documenti")
        self.tabs.addTab(self._build_params_tab(), "Parametri")
        self.setCentralWidget(self.tabs)
        self.kb_label = QLabel()
        self.statusBar().addPermanentWidget(self.kb_label)

    def _build_docs_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        row = QHBoxLayout()
        for text, slot in [("Importa documenti…", self.import_dialog),
                           ("Importa cartella…", self.import_folder_dialog),
                           ("Rimuovi", self.remove_selected),
                           ("Rianalizza tutto", self.reanalyze_all)]:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        hint = QLabel("Suggerimento: puoi trascinare PDF/TXT/MD nella finestra.")
        hint.setObjectName("hint")
        row.addWidget(hint)
        layout.addLayout(row)

        split = QSplitter(Qt.Orientation.Vertical)
        self.docs_table = _table(["Titolo", "Data", "Fonte", "Insight", "Flag"])
        self.docs_table.itemSelectionChanged.connect(self._show_doc_insights)
        split.addWidget(self.docs_table)
        self.insights_table = _table(["Categoria", "Parametro", "Valore", "Pag.", "Evidenza"])
        split.addWidget(self.insights_table)
        split.setSizes([260, 460])
        layout.addWidget(split)
        return w

    def _build_params_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        hint = QLabel("Per ogni parametro vale il documento più recente; i valori diversi di "
                      "altri documenti sono indicati come conflitti.")
        hint.setObjectName("hint")
        layout.addWidget(hint)
        self.params_table = _table(["Parametro", "Valore", "Fonte", "Data", "Conflitti"])
        layout.addWidget(self.params_table)
        return w

    def _money_spin(self, maximum: float = 10_000_000, special: bool = False) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, maximum)
        spin.setDecimals(0)
        spin.setGroupSeparatorShown(True)
        spin.setSingleStep(100)
        if special:
            spin.setSpecialValueText("n/d")
        return spin

    def _build_plan_tab(self) -> QWidget:
        split = QSplitter(Qt.Orientation.Horizontal)
        form_host = QWidget()
        col = QVBoxLayout(form_host)

        box = QGroupBox("Capitale e mercato")
        form = QFormLayout(box)
        self.capital = self._money_spin(1_000_000_000)
        self.currency = QComboBox()
        self.currency.addItems(["EUR", "USD"])
        self.currency.currentTextChanged.connect(self._currency_changed)
        self.fx = QDoubleSpinBox()
        self.fx.setRange(0.01, 100)
        self.fx.setDecimals(4)
        self.fx.setSingleStep(0.01)
        self.price = self._money_spin()
        self.market_btn = QPushButton("Aggiorna dati di mercato")
        self.market_btn.clicked.connect(self.refresh_market)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd/MM/yyyy")
        form.addRow("Capitale", self.capital)
        form.addRow("Valuta", self.currency)
        form.addRow("USD per 1 unità", self.fx)
        form.addRow("Prezzo BTC (USD)", self.price)
        form.addRow("", self.market_btn)
        form.addRow("Data", self.date)
        col.addWidget(box)

        box = QGroupBox("Strategia")
        form = QFormLayout(box)
        self.profile = QComboBox()
        self.profile.addItems(list(PROFILES))
        self.bottom_pct = QDoubleSpinBox()
        self.bottom_pct.setRange(-1, 100)
        self.bottom_pct.setDecimals(0)
        self.bottom_pct.setSuffix(" %")
        self.bottom_pct.setSpecialValueText("da profilo")
        self.repeg = QCheckBox("Riancora ladder al floor attuale")
        self.slow_drip = QCheckBox("Drip lento (metà)")
        form.addRow("Profilo", self.profile)
        form.addRow("Quota finestra minimo", self.bottom_pct)
        form.addRow(self.repeg)
        form.addRow(self.slow_drip)
        col.addWidget(box)

        box = QGroupBox("Indicatori (opzionali)")
        form = QFormLayout(box)
        self.fear = QSpinBox()
        self.fear.setRange(-1, 100)
        self.fear.setSpecialValueText("n/d")
        self.ma200 = self._money_spin(special=True)
        self.high200 = self._money_spin(special=True)
        self.vix = QDoubleSpinBox()
        self.vix.setRange(0, 200)
        self.vix.setSpecialValueText("n/d")
        self.low_close = self._money_spin(special=True)
        form.addRow("Fear && Greed", self.fear)
        form.addRow("MA 200 giorni", self.ma200)
        form.addRow("Massimo 200 giorni", self.high200)
        form.addRow("VIX", self.vix)
        form.addRow("Minimo chiusura ciclo", self.low_close)
        col.addWidget(box)

        self.generate_btn = QPushButton("Genera piano")
        self.generate_btn.setObjectName("primary")
        self.generate_btn.clicked.connect(self.generate_plan)
        col.addWidget(self.generate_btn)
        row = QHBoxLayout()
        for text, fmt in (("Esporta HTML", "html"), ("Esporta Markdown", "md")):
            btn = QPushButton(text)
            btn.clicked.connect(lambda _=False, f=fmt: self.export_plan(f))
            row.addWidget(btn)
        col.addLayout(row)
        col.addStretch(1)

        # Frecce degli spinbox non stilizzabili in modo pulito via QSS: input da tastiera/rotella
        for spin in form_host.findChildren(QAbstractSpinBox):
            if not isinstance(spin, QDateEdit):
                spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        scroll = QScrollArea()
        scroll.setWidget(form_host)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(370)
        split.addWidget(scroll)
        self.report = QTextBrowser()
        self.report.setOpenExternalLinks(True)
        self.report.setHtml("<p style='color:#6b7280'>Importa i documenti e premi "
                            "<b>Genera piano</b>.</p>")
        split.addWidget(self.report)
        split.setSizes([380, 900])
        return split

    def _currency_changed(self, currency: str) -> None:
        self.fx.setEnabled(currency != "USD")
        if currency == "USD":
            self.fx.setValue(1.0)

    # ---------------------------------------------------------------- settings
    def _load_settings(self) -> None:
        s = self.settings
        self.capital.setValue(float(s.value("capital", 10000)))
        self.currency.setCurrentText(s.value("currency", "EUR"))
        self.fx.setValue(float(s.value("fx", 1.17)))
        self._currency_changed(self.currency.currentText())
        self.price.setValue(float(s.value("price", 0)))
        self.profile.setCurrentText(s.value("profile", "bilanciato"))
        self.bottom_pct.setValue(float(s.value("bottom_pct", -1)))
        self.repeg.setChecked(s.value("repeg", "true") in (True, "true"))
        self.slow_drip.setChecked(s.value("slow_drip", "false") in (True, "true"))
        self.fear.setValue(int(s.value("fear", -1)))
        self.ma200.setValue(float(s.value("ma200", 0)))
        self.high200.setValue(float(s.value("high200", 0)))
        self.vix.setValue(float(s.value("vix", 0)))
        self.low_close.setValue(float(s.value("low_close", 0)))

    def _save_settings(self) -> None:
        s = self.settings
        for key, value in [("capital", self.capital.value()), ("currency", self.currency.currentText()),
                           ("fx", self.fx.value()), ("price", self.price.value()),
                           ("profile", self.profile.currentText()),
                           ("bottom_pct", self.bottom_pct.value()),
                           ("repeg", self.repeg.isChecked()), ("slow_drip", self.slow_drip.isChecked()),
                           ("fear", self.fear.value()), ("ma200", self.ma200.value()),
                           ("high200", self.high200.value()), ("vix", self.vix.value()),
                           ("low_close", self.low_close.value())]:
            s.setValue(key, value)

    def closeEvent(self, event) -> None:
        self._save_settings()
        super().closeEvent(event)

    # --------------------------------------------------------------- documenti
    def _on_kb_loaded(self, kb: KnowledgeBase, error: str = "") -> None:
        self.kb = kb
        self.refresh_views()
        if error:
            QMessageBox.warning(self, "Knowledge base", f"Impossibile leggere i dati salvati:\n{error}")
        self.statusBar().showMessage("Pronto.", 4000)
        if self.price.value() > 0 and self.kb.documents:
            self.generate_plan()

    def import_dialog(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Importa documenti", "", FILE_FILTER)
        if files:
            self.import_paths(files)

    def import_folder_dialog(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Importa cartella")
        if folder:
            self.import_paths([folder])

    def import_paths(self, paths: List[str]) -> None:
        dlg = QProgressDialog("Analisi dei documenti…", None, 0, 100, self)
        dlg.setWindowTitle("Importazione")
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(300)

        def done(result) -> None:
            dlg.close()
            docs, errors = result
            added = sum(self.kb.add(d) for d in docs)
            self.refresh_views()
            self._save_kb()
            msg = f"Importati {added} nuovi documenti ({len(docs) - added} aggiornati)."
            self.statusBar().showMessage(msg, 6000)
            if errors:
                QMessageBox.warning(self, "Importazione", msg + "\n\nErrori:\n" + "\n".join(errors))
            if docs:
                self.generate_plan(silent=True)

        def failed(err: str) -> None:
            dlg.close()
            QMessageBox.critical(self, "Importazione", err)

        self._run(import_files, paths, ok=done, fail=failed,
                  progress=lambda v, name: (dlg.setValue(v), dlg.setLabelText(f"Analisi: {name}")))

    def remove_selected(self) -> None:
        row = self.docs_table.currentRow()
        if row < 0:
            return
        doc = self.kb.sorted_documents()[row]
        if QMessageBox.question(self, "Rimuovi", f"Rimuovere «{doc.title}»?") != \
                QMessageBox.StandardButton.Yes:
            return
        self.kb.remove(doc.doc_id)
        self.refresh_views()
        self._save_kb()

    def reanalyze_all(self) -> None:
        def done(kb: KnowledgeBase) -> None:
            self.kb = kb
            self.refresh_views()
            self._save_kb()
            self.statusBar().showMessage("Documenti rianalizzati.", 4000)

        self._run(reanalyzed_copy, self.kb.to_json(), ok=done,
                  fail=lambda e: QMessageBox.warning(self, "Rianalisi", e))

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        paths = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if paths:
            self.import_paths(paths)

    def refresh_views(self) -> None:
        docs = self.kb.sorted_documents()
        self.docs_table.setRowCount(len(docs))
        for r, d in enumerate(docs):
            vals = [d.title, self.kb.effective_date(d), d.source, len(d.insights),
                    "; ".join(d.flags)]
            for c, v in enumerate(vals):
                self.docs_table.setItem(r, c, _item(v, align_right=(c == 3)))
        _fit(self.docs_table)
        self.insights_table.setRowCount(0)

        params = self.kb.effective_params()
        self.params_table.setRowCount(len(params))
        for r, p in enumerate(sorted(params.values(), key=lambda x: x.key)):
            conflicts = "; ".join(f"{_fmt(a['value'])} ({a['doc_title']})"
                                  for a in p.alternatives if a["value"] != p.value)
            for c, v in enumerate([p.label, _fmt(p.value), p.doc_title, p.doc_date or "",
                                   conflicts]):
                cell = _item(v)
                cell.setToolTip(str(v))
                self.params_table.setItem(r, c, cell)
        _fit(self.params_table)
        self.kb_label.setText(f"Documenti: {len(docs)} · Parametri: {len(params)}")

    def _show_doc_insights(self) -> None:
        row = self.docs_table.currentRow()
        docs = self.kb.sorted_documents()
        if not 0 <= row < len(docs):
            return
        ins = docs[row].insights
        self.insights_table.setRowCount(len(ins))
        for r, i in enumerate(ins):
            for c, v in enumerate([i.category, i.label, _fmt(i.value), i.page, i.evidence]):
                cell = _item(v, align_right=(c == 3))
                cell.setToolTip(i.evidence if c == 4 else _fmt(i.value))
                self.insights_table.setItem(r, c, cell)
        _fit(self.insights_table)
        self.insights_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch)

    # ------------------------------------------------------------------ mercato
    def refresh_market(self) -> None:
        self.market_btn.setEnabled(False)
        self.statusBar().showMessage("Download dati di mercato…")

        def done(snap: MarketSnapshot) -> None:
            self.market_btn.setEnabled(True)
            if snap.price_usd:
                self.price.setValue(snap.price_usd)
            if snap.usd_per_eur and self.currency.currentText() == "EUR":
                self.fx.setValue(snap.usd_per_eur)
            for spin, value in ((self.ma200, snap.ma200), (self.high200, snap.high200),
                                (self.low_close, snap.cycle_low_close)):
                if value:
                    spin.setValue(value)
            if snap.fear_greed is not None:
                self.fear.setValue(snap.fear_greed)
            if snap.errors and not snap.price_usd:
                QMessageBox.warning(self, "Dati di mercato",
                                    "Download non riuscito:\n" + "\n".join(snap.errors))
            else:
                self.statusBar().showMessage(
                    "Dati di mercato aggiornati" + (" (parziali)" if snap.errors else "") + ".", 5000)
                self.date.setDate(QDate.currentDate())
                self.generate_plan(silent=True)

        def failed(err: str) -> None:
            self.market_btn.setEnabled(True)
            QMessageBox.warning(self, "Dati di mercato", err)

        self._run(fetch_market, ok=done, fail=failed)

    # -------------------------------------------------------------------- piano
    def _inputs(self) -> PlanInputs:
        def opt(spin) -> Optional[float]:
            return spin.value() if spin.value() > spin.minimum() else None

        fear = self.fear.value()
        return PlanInputs(
            capital=self.capital.value(),
            btc_price_usd=self.price.value(),
            currency=self.currency.currentText(),
            usd_per_unit=self.fx.value(),
            today=self.date.date().toPyDate(),
            profile=self.profile.currentText(),
            bottom_pot_pct=self.bottom_pct.value() if self.bottom_pct.value() >= 0 else None,
            repeg_ladder=self.repeg.isChecked(),
            slow_drip=self.slow_drip.isChecked(),
            fear_greed=fear if fear >= 0 else None,
            ma200=opt(self.ma200),
            high200=opt(self.high200),
            vix=opt(self.vix),
            cycle_low_close=opt(self.low_close),
        )

    def generate_plan(self, silent: bool = False) -> None:
        try:
            self.plan = Planner(self.kb).build(self._inputs())
        except ValueError as exc:
            if not silent:
                QMessageBox.warning(self, "Piano", str(exc))
            return
        self.report.setHtml(render_html(self.plan))
        self.tabs.setCurrentIndex(0)
        self._save_settings()
        self.statusBar().showMessage("Piano generato.", 4000)

    def export_plan(self, fmt: str) -> None:
        if not self.plan:
            QMessageBox.information(self, "Esporta", "Genera prima un piano.")
            return
        ext = "html" if fmt == "html" else "md"
        default = f"piano_btc_{self.plan.inputs.today:%Y%m%d}.{ext}"
        path, _ = QFileDialog.getSaveFileName(self, "Esporta piano", default,
                                              f"{ext.upper()} (*.{ext})")
        if not path:
            return
        text = render_html(self.plan) if fmt == "html" else render_markdown(self.plan)
        self._run(lambda p, t: Path(p).write_text(t, encoding="utf-8"), path, text,
                  ok=lambda _: self.statusBar().showMessage(f"Esportato: {path}", 6000),
                  fail=lambda e: QMessageBox.critical(self, "Esporta", e))

    # -------------------------------------------------------------- aggiornamenti
    def check_updates(self, manual: bool) -> None:
        if self._update_busy:
            return
        self._update_busy = True

        def done(release) -> None:
            self._update_busy = False
            if release is None:
                if manual:
                    QMessageBox.information(self, "Aggiornamenti",
                                            f"Nessun aggiornamento: la versione {self.version} "
                                            "è la più recente.")
                return
            if ask_update(self, release, self.version):
                self._download_update(release)

        def failed(err: str) -> None:
            self._update_busy = False
            if manual:
                QMessageBox.warning(self, "Aggiornamenti", f"Controllo non riuscito:\n{err}")

        self._run(updater.check_for_update, self.version, GITHUB_REPO, ok=done, fail=failed)

    def _download_update(self, release: updater.ReleaseInfo) -> None:
        asset = updater.select_asset(release.assets)
        if not asset:
            QDesktopServices.openUrl(QUrl(release.html_url))
            return
        dest = Path(tempfile.gettempdir()) / "BTC_Cycle_update" / asset["name"]
        dlg = QProgressDialog(f"Download {asset['name']}…", None, 0, 100, self)
        dlg.setWindowTitle("Aggiornamento")
        dlg.setMinimumDuration(0)

        def done(path: Path) -> None:
            dlg.close()
            if updater.launch_installer(path):
                self.close()
                return
            QMessageBox.information(self, "Aggiornamento",
                                    f"Scaricato in:\n{path}\n\nChiudi l'app e sostituisci "
                                    "l'eseguibile con quello nuovo.")
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

        def failed(err: str) -> None:
            dlg.close()
            QMessageBox.critical(self, "Aggiornamento", f"Download non riuscito:\n{err}")

        self._run(updater.download, asset["url"], dest, ok=done, fail=failed,
                  progress=lambda v, _m: dlg.setValue(v))

    def show_about(self) -> None:
        QMessageBox.about(
            self, f"Informazioni su {APP_NAME}",
            f"<h3>{APP_NAME}</h3><p>Versione {self.version}</p><p>Autore: {APP_AUTHOR}</p>"
            f"<p>Analizza documenti sul ciclo di Bitcoin e genera un piano di investimento.</p>"
            f"<p><a href='https://github.com/{GITHUB_REPO}'>github.com/{GITHUB_REPO}</a></p>"
            "<p><i>Strumento educativo, non consulenza finanziaria.</i></p>",
        )
