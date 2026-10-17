"""Finestra principale: piano e grafico; documenti/parametri in Strumenti; menu e aggiornamenti."""

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
    QDialog,
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
from ..guide import build_guide_pdf
from ..i18n import LANGUAGES, get_lang, tr, tr_label
from ..paths import data_dir, knowledge_path, read_version
from .chart_tab import ChartTab
from .dialogs import HelpDialog, ask_update
from .workers import TaskWorker


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
        self.statusBar().showMessage(tr("Caricamento knowledge base…"))

        self._run(KnowledgeBase.load, knowledge_path(), ok=self._on_kb_loaded,
                  fail=lambda e: self._on_kb_loaded(KnowledgeBase(), e))
        QTimer.singleShot(3000, lambda: self.check_updates(manual=False))

    # ------------------------------------------------------------------ worker
    def _run(self, fn: Callable, *args, ok: Callable, fail: Optional[Callable] = None,
             progress: Optional[Callable] = None) -> TaskWorker:
        worker = TaskWorker(fn, *args, with_progress=progress is not None, parent=self)
        worker.succeeded.connect(ok)
        worker.failed.connect(fail or (lambda e: self.statusBar().showMessage(tr("Errore: {e}").format(e=e))))
        if progress:
            worker.progress.connect(progress)
        worker.finished.connect(lambda: self._workers.discard(worker))
        self._workers.add(worker)
        worker.start()
        return worker

    def _save_kb(self) -> None:
        text = self.kb.to_json()
        self._run(KnowledgeBase.save_text, knowledge_path(), text, ok=lambda _: None,
                  fail=lambda e: QMessageBox.warning(self, tr("Salvataggio"),
                                                 tr("Impossibile salvare: {e}").format(e=e)))

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
        m = bar.addMenu(tr("&File"))
        self._action(m, tr("Importa documenti…"), self.import_dialog, QKeySequence.StandardKey.Open)
        self._action(m, tr("Importa cartella…"), self.import_folder_dialog)
        m.addSeparator()
        self._action(m, tr("Esporta piano (HTML)…"), lambda: self.export_plan("html"))
        self._action(m, tr("Esporta piano (Markdown)…"), lambda: self.export_plan("md"))
        m.addSeparator()
        self._action(m, tr("Esci"), self.close, QKeySequence.StandardKey.Quit)

        m = bar.addMenu(tr("&Dati"))
        self._action(m, tr("Aggiorna dati di mercato"), self.refresh_market, "F5")
        self._action(m, tr("Genera piano"), self.generate_plan, "Ctrl+G")
        self._action(m, tr("Rianalizza tutti i documenti"), self.reanalyze_all)
        self._action(m, tr("Rimuovi documento selezionato"), self.remove_selected)
        self._action(m, tr("Apri cartella dati"), lambda: QDesktopServices.openUrl(
            QUrl.fromLocalFile(str(data_dir()))))

        m = bar.addMenu(tr("&Strumenti"))
        self._action(m, tr("Documenti e parametri…"), self.show_tools)
        lang_menu = m.addMenu(tr("Lingua"))
        self._lang_actions = {}
        for code, name in LANGUAGES.items():
            act = QAction(name, self, checkable=True, checked=code == get_lang())
            act.triggered.connect(lambda _=False, c=code: self.set_language(c))
            lang_menu.addAction(act)
            self._lang_actions[code] = act

        m = bar.addMenu(tr("&Aiuto"))
        self._action(m, tr("Guida"), self.open_guide, "F1")
        self._action(m, tr("Controlla aggiornamenti"), lambda: self.check_updates(manual=True))
        m.addSeparator()
        self._action(m, tr("Informazioni"), self.show_about)

    # ---------------------------------------------------------------------- UI
    def _build_ui(self) -> None:
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_plan_tab(), tr("Piano"))
        self.chart_tab = ChartTab(self._run)
        self.tabs.addTab(self.chart_tab, tr("Grafico"))
        self.setCentralWidget(self.tabs)
        self.tools = QDialog(self)
        self.tools.setWindowTitle(tr("Documenti e parametri…").rstrip("…"))
        self.tools.resize(1000, 640)
        tool_tabs = QTabWidget()
        tool_tabs.addTab(self._build_docs_tab(), tr("Documenti"))
        tool_tabs.addTab(self._build_params_tab(), tr("Parametri"))
        QVBoxLayout(self.tools).addWidget(tool_tabs)
        self.kb_label = QLabel()
        self.statusBar().addPermanentWidget(self.kb_label)

    def set_language(self, code: str) -> None:
        # shortcut: la lingua si applica al riavvio, la GUI non si ricostruisce a caldo
        self.settings.setValue("lang", code)
        QMessageBox.information(self, tr("Lingua"),
                                tr("La lingua cambierà al prossimo avvio dell'applicazione."))
        for c, act in self._lang_actions.items():
            act.setChecked(c == code)

    def open_guide(self) -> None:
        """Genera (una volta per versione e lingua) e apre la guida PDF; se fallisce, guida breve."""
        def done(path: str) -> None:
            if not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                QMessageBox.information(self, tr("Guida"), tr("Guida salvata in:\n{path}").format(path=path))

        def failed(err: str) -> None:
            self.statusBar().showMessage(tr("Errore: {e}").format(e=err), 6000)
            HelpDialog(self).exec()

        self._run(build_guide_pdf, get_lang(), ok=done, fail=failed)

    def show_tools(self) -> None:
        self.tools.show()
        self.tools.raise_()

    def _build_docs_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        row = QHBoxLayout()
        for text, slot in [(tr("Importa documenti…"), self.import_dialog),
                           (tr("Importa cartella…"), self.import_folder_dialog),
                           (tr("Rimuovi"), self.remove_selected),
                           (tr("Rianalizza tutto"), self.reanalyze_all)]:
            btn = QPushButton(text)
            btn.clicked.connect(slot)
            row.addWidget(btn)
        row.addStretch(1)
        hint = QLabel(tr("Suggerimento: puoi trascinare PDF/TXT/MD nella finestra."))
        hint.setObjectName("hint")
        row.addWidget(hint)
        layout.addLayout(row)

        split = QSplitter(Qt.Orientation.Vertical)
        self.docs_table = _table([tr(h) for h in ("Titolo", "Data", "Fonte", "Insight", "Flag")])
        self.docs_table.itemSelectionChanged.connect(self._show_doc_insights)
        split.addWidget(self.docs_table)
        self.insights_table = _table([tr(h) for h in ("Categoria", "Parametro", "Valore", "Pag.",
                                                      "Evidenza")])
        split.addWidget(self.insights_table)
        split.setSizes([260, 460])
        layout.addWidget(split)
        return w

    def _build_params_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        hint = QLabel(tr("Per ogni parametro vale il documento più recente; i valori diversi di "
                         "altri documenti sono indicati come conflitti."))
        hint.setObjectName("hint")
        layout.addWidget(hint)
        self.params_table = _table([tr(h) for h in ("Parametro", "Valore", "Fonte", "Data", "Conflitti")])
        layout.addWidget(self.params_table)
        return w

    def _money_spin(self, maximum: float = 10_000_000, special: bool = False) -> QDoubleSpinBox:
        spin = QDoubleSpinBox()
        spin.setRange(0, maximum)
        spin.setDecimals(0)
        spin.setGroupSeparatorShown(True)
        spin.setSingleStep(100)
        if special:
            spin.setSpecialValueText(tr("n/d"))
        return spin

    def _build_plan_tab(self) -> QWidget:
        split = QSplitter(Qt.Orientation.Horizontal)
        form_host = QWidget()
        col = QVBoxLayout(form_host)

        box = QGroupBox(tr("Capitale e mercato"))
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
        self.market_btn = QPushButton(tr("Aggiorna dati di mercato"))
        self.market_btn.clicked.connect(self.refresh_market)
        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd/MM/yyyy")
        form.addRow(tr("Capitale"), self.capital)
        form.addRow(tr("Valuta"), self.currency)
        form.addRow(tr("USD per 1 unità"), self.fx)
        form.addRow(tr("Prezzo BTC (USD)"), self.price)
        form.addRow("", self.market_btn)
        form.addRow(tr("Data"), self.date)
        col.addWidget(box)

        box = QGroupBox(tr("Strategia"))
        form = QFormLayout(box)
        self.profile = QComboBox()
        for name in PROFILES:
            self.profile.addItem(tr(name), name)  # il dato resta la chiave italiana usata dal motore
        self.bottom_pct = QDoubleSpinBox()
        self.bottom_pct.setRange(-1, 100)
        self.bottom_pct.setDecimals(0)
        self.bottom_pct.setSuffix(" %")
        self.bottom_pct.setSpecialValueText(tr("da profilo"))
        self.repeg = QCheckBox(tr("Riancora ladder al floor attuale"))
        self.slow_drip = QCheckBox(tr("Drip lento (metà)"))
        form.addRow(tr("Profilo"), self.profile)
        form.addRow(tr("Quota finestra minimo"), self.bottom_pct)
        form.addRow(self.repeg)
        form.addRow(self.slow_drip)
        col.addWidget(box)

        box = QGroupBox(tr("Indicatori (opzionali)"))
        form = QFormLayout(box)
        self.fear = QSpinBox()
        self.fear.setRange(-1, 100)
        self.fear.setSpecialValueText(tr("n/d"))
        self.ma200 = self._money_spin(special=True)
        self.high200 = self._money_spin(special=True)
        self.vix = QDoubleSpinBox()
        self.vix.setRange(0, 200)
        self.vix.setSpecialValueText(tr("n/d"))
        self.low_close = self._money_spin(special=True)
        form.addRow("Fear && Greed", self.fear)
        form.addRow(tr("MA 200 giorni"), self.ma200)
        form.addRow(tr("Massimo 200 giorni"), self.high200)
        form.addRow("VIX", self.vix)
        form.addRow(tr("Minimo chiusura ciclo"), self.low_close)
        col.addWidget(box)

        self.generate_btn = QPushButton(tr("Genera piano"))
        self.generate_btn.setObjectName("primary")
        self.generate_btn.clicked.connect(self.generate_plan)
        col.addWidget(self.generate_btn)
        row = QHBoxLayout()
        for text, fmt in ((tr("Esporta HTML"), "html"), (tr("Esporta Markdown"), "md")):
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
        self.report.setHtml(tr("<p style='color:#6b7280'>Importa i documenti e premi "
                               "<b>Genera piano</b>.</p>"))
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
        self.profile.setCurrentIndex(max(0, self.profile.findData(s.value("profile", "bilanciato"))))
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
                           ("profile", self.profile.currentData()),
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
            QMessageBox.warning(self, "Knowledge base",
                                tr("Impossibile leggere i dati salvati:\n{error}").format(error=error))
        self.statusBar().showMessage(tr("Pronto."), 4000)
        if self.price.value() > 0 and self.kb.documents:
            self.generate_plan()

    def import_dialog(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, tr("Importa documenti"), "",
            tr("Documenti (*.pdf *.txt *.md);;PDF (*.pdf);;Tutti i file (*)"))
        if files:
            self.import_paths(files)

    def import_folder_dialog(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("Importa cartella"))
        if folder:
            self.import_paths([folder])

    def import_paths(self, paths: List[str]) -> None:
        dlg = QProgressDialog(tr("Analisi dei documenti…"), None, 0, 100, self)
        dlg.setWindowTitle(tr("Importazione"))
        dlg.setWindowModality(Qt.WindowModality.WindowModal)
        dlg.setMinimumDuration(300)

        def done(result) -> None:
            dlg.close()
            docs, errors = result
            added = sum(self.kb.add(d) for d in docs)
            self.refresh_views()
            self._save_kb()
            msg = tr("Importati {added} nuovi documenti ({updated} aggiornati).").format(
                added=added, updated=len(docs) - added)
            self.statusBar().showMessage(msg, 6000)
            if errors:
                QMessageBox.warning(self, tr("Importazione"),
                                    msg + tr("\n\nErrori:\n") + "\n".join(errors))
            if docs:
                self.generate_plan(silent=True)

        def failed(err: str) -> None:
            dlg.close()
            QMessageBox.critical(self, tr("Importazione"), err)

        self._run(import_files, paths, ok=done, fail=failed,
                  progress=lambda v, name: (dlg.setValue(v),
                                           dlg.setLabelText(tr("Analisi: {name}").format(name=name))))

    def remove_selected(self) -> None:
        row = self.docs_table.currentRow()
        if row < 0:
            return
        doc = self.kb.sorted_documents()[row]
        if QMessageBox.question(self, tr("Rimuovi"),
                                 tr("Rimuovere «{title}»?").format(title=doc.title)) != \
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
            self.statusBar().showMessage(tr("Documenti rianalizzati."), 4000)

        self._run(reanalyzed_copy, self.kb.to_json(), ok=done,
                  fail=lambda e: QMessageBox.warning(self, tr("Rianalisi"), e))

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
            vals = [d.title, self.kb.effective_date(d), tr(d.source), len(d.insights),
                    "; ".join(tr(f) for f in d.flags)]
            for c, v in enumerate(vals):
                self.docs_table.setItem(r, c, _item(v, align_right=(c == 3)))
        _fit(self.docs_table)
        self.insights_table.setRowCount(0)

        params = self.kb.effective_params()
        self.params_table.setRowCount(len(params))
        for r, p in enumerate(sorted(params.values(), key=lambda x: x.key)):
            conflicts = "; ".join(f"{_fmt(a['value'])} ({a['doc_title']})"
                                  for a in p.alternatives if a["value"] != p.value)
            for c, v in enumerate([tr_label(p.label), _fmt(p.value), p.doc_title, p.doc_date or "",
                                   conflicts]):
                cell = _item(v)
                cell.setToolTip(str(v))
                self.params_table.setItem(r, c, cell)
        _fit(self.params_table)
        self.kb_label.setText(tr("Documenti: {d} · Parametri: {p}").format(d=len(docs), p=len(params)))

    def _show_doc_insights(self) -> None:
        row = self.docs_table.currentRow()
        docs = self.kb.sorted_documents()
        if not 0 <= row < len(docs):
            return
        ins = docs[row].insights
        self.insights_table.setRowCount(len(ins))
        for r, i in enumerate(ins):
            for c, v in enumerate([i.category, tr_label(i.label), _fmt(i.value), i.page, i.evidence]):
                cell = _item(v, align_right=(c == 3))
                cell.setToolTip(i.evidence if c == 4 else _fmt(i.value))
                self.insights_table.setItem(r, c, cell)
        _fit(self.insights_table)
        self.insights_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeMode.Stretch)

    # ------------------------------------------------------------------ mercato
    def refresh_market(self) -> None:
        self.market_btn.setEnabled(False)
        self.statusBar().showMessage(tr("Download dati di mercato…"))

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
                QMessageBox.warning(self, tr("Dati di mercato"), tr("Download non riuscito:\n{errors}")
                                    .format(errors="\n".join(snap.errors)))
            else:
                self.statusBar().showMessage(
                    tr("Dati di mercato aggiornati") + (tr(" (parziali)") if snap.errors else "") + ".", 5000)
                self.date.setDate(QDate.currentDate())
                self.generate_plan(silent=True)

        def failed(err: str) -> None:
            self.market_btn.setEnabled(True)
            QMessageBox.warning(self, tr("Dati di mercato"), err)

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
            profile=self.profile.currentData(),
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
                QMessageBox.warning(self, tr("Piano"), str(exc))
            return
        self.report.setHtml(render_html(self.plan))
        self.chart_tab.set_plan(self.plan)
        if not silent:
            self.tabs.setCurrentIndex(0)
        self._save_settings()
        self.statusBar().showMessage(tr("Piano generato."), 4000)

    def export_plan(self, fmt: str) -> None:
        if not self.plan:
            QMessageBox.information(self, tr("Esporta"), tr("Genera prima un piano."))
            return
        ext = "html" if fmt == "html" else "md"
        default = f"piano_btc_{self.plan.inputs.today:%Y%m%d}.{ext}"
        path, _ = QFileDialog.getSaveFileName(self, tr("Esporta piano"), default,
                                              f"{ext.upper()} (*.{ext})")
        if not path:
            return
        text = render_html(self.plan) if fmt == "html" else render_markdown(self.plan)
        self._run(lambda p, t: Path(p).write_text(t, encoding="utf-8"), path, text,
                  ok=lambda _: self.statusBar().showMessage(tr("Esportato: {path}").format(path=path), 6000),
                  fail=lambda e: QMessageBox.critical(self, tr("Esporta"), e))

    # -------------------------------------------------------------- aggiornamenti
    def check_updates(self, manual: bool) -> None:
        if self._update_busy:
            return
        self._update_busy = True

        def done(release) -> None:
            self._update_busy = False
            if release is None:
                if manual:
                    QMessageBox.information(self, tr("Aggiornamenti"),
                                            tr("Nessun aggiornamento: la versione {v} è la più recente.")
                                            .format(v=self.version))
                return
            if ask_update(self, release, self.version):
                self._download_update(release)

        def failed(err: str) -> None:
            self._update_busy = False
            if manual:
                QMessageBox.warning(self, tr("Aggiornamenti"),
                                    tr("Controllo non riuscito:\n{err}").format(err=err))

        self._run(updater.check_for_update, self.version, GITHUB_REPO, ok=done, fail=failed)

    def _download_update(self, release: updater.ReleaseInfo) -> None:
        asset = updater.select_asset(release.assets)
        if not asset:
            QDesktopServices.openUrl(QUrl(release.html_url))
            return
        dest = Path(tempfile.gettempdir()) / "BTC_Cycle_update" / asset["name"]
        dlg = QProgressDialog(tr("Download {name}…").format(name=asset["name"]), None, 0, 100, self)
        dlg.setWindowTitle(tr("Aggiornamento"))
        dlg.setMinimumDuration(0)

        def done(path: Path) -> None:
            dlg.close()
            if updater.launch_installer(path):
                self.close()
                return
            QMessageBox.information(
                self, tr("Aggiornamento"),
                tr("Scaricato in:\n{path}\n\nChiudi l'app e sostituisci l'eseguibile con quello nuovo.")
                .format(path=path))
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))

        def failed(err: str) -> None:
            dlg.close()
            QMessageBox.critical(self, tr("Aggiornamento"),
                                 tr("Download non riuscito:\n{err}").format(err=err))

        self._run(updater.download, asset["url"], dest, ok=done, fail=failed,
                  progress=lambda v, _m: dlg.setValue(v))

    def show_about(self) -> None:
        QMessageBox.about(
            self, tr("Informazioni su {app}").format(app=APP_NAME),
            f"<h3>{APP_NAME}</h3><p>{tr('Versione {v}').format(v=self.version)}</p>"
            f"<p>{tr('Autore: {a}').format(a=APP_AUTHOR)}</p>"
            f"<p>{tr('Analizza documenti sul ciclo di Bitcoin e genera un piano di investimento.')}</p>"
            f"<p><a href='https://github.com/{GITHUB_REPO}'>github.com/{GITHUB_REPO}</a></p>"
            f"<p><i>{tr('Strumento educativo, non consulenza finanziaria.')}</i></p>",
        )
