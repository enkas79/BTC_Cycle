"""Scheda grafico: prezzo BTC con i livelli e le finestre della strategia."""

from __future__ import annotations

import math
from datetime import date, datetime, time, timedelta
from typing import Callable, List, Optional, Tuple

import pyqtgraph as pg
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ..core.chart import FAILED_RALLY_MEDIAN_PCT, build_overlays, nearest_zone, rally_from_low
from ..core.cycles import cycle_series
from ..core.market import fetch_history, fetch_spot
from ..core.planner import Plan, usd
from ..i18n import fmt_date, tr
from .style import ACCENT_DARK, INK

POLL_MS = 60_000  # CoinGecko gratuito: ~30 chiamate/min, 1/min è ampiamente nei limiti
FUTURE_DAYS = 365
LEVEL_COLORS = {"floor": "#1b5e20", "fair": "#6b7280", "rialzo": "#c62828",
                "ribasso": "#c62828", "ma200": "#1565c0"}


def _ts(d: date) -> float:
    return datetime.combine(d, time()).timestamp()


def _pen(color: str, width: int = 1, dash: bool = False):
    pen = pg.mkPen(color=color, width=width)
    if dash:
        pen.setStyle(pg.QtCore.Qt.PenStyle.DashLine)
    return pen


class ChartTab(QWidget):
    """``run`` è il lancio-worker della finestra: nessuna rete nel thread GUI."""

    def __init__(self, run: Callable, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._run = run
        self.plan: Optional[Plan] = None
        self.history: List[Tuple[float, float]] = []
        self.full_history: List[Tuple[float, float]] = []  # dal 2010, per i cicli sovrapposti
        self.spot: Optional[float] = None
        self._click: Optional[Tuple[float, float]] = None  # (timestamp, prezzo) del punto cliccato
        self._busy = False
        self._status = ""

        pg.setConfigOptions(antialias=True, background="w", foreground=INK)
        self.plot = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem()})
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setMenuEnabled(False)
        self.plot.getAxis("left").setLabel("USD")
        self.plot.scene().sigMouseClicked.connect(self._on_click)

        self.cycle_plot = pg.PlotWidget()
        self.cycle_plot.showGrid(x=True, y=True, alpha=0.15)
        self.cycle_plot.setMenuEnabled(False)
        self.cycle_plot.getAxis("bottom").setLabel(tr("giorni dall'halving"))
        self.cycle_plot.getAxis("left").setLabel(tr("prezzo / prezzo all'halving"))
        self.stack = QStackedWidget()
        self.stack.addWidget(self.plot)
        self.stack.addWidget(self.cycle_plot)

        self.info = QLabel(tr("Genera un piano per vedere livelli e finestre della strategia."))
        self.info.setObjectName("hint")
        self.info.setWordWrap(True)
        self.sources = QLabel()
        self.sources.setObjectName("hint")
        self.sources.setWordWrap(True)
        refresh = QPushButton(tr("Aggiorna storico"))
        refresh.clicked.connect(self.load_history)
        reset = QPushButton(tr("Reimposta vista"))
        reset.clicked.connect(lambda: self._redraw(reset_view=True))

        self.log_box = QCheckBox(tr("Scala logaritmica"))
        self.log_box.setChecked(str(QSettings("enkas79", "BTC_Cycle").value("chart_log", "false")) == "true")
        self.log_box.toggled.connect(self._toggle_log)
        self.exit_box = QCheckBox(tr("Mostra uscite"))
        saved = QSettings("enkas79", "BTC_Cycle").value("chart_exits", "false")
        self.exit_box.setChecked(str(saved) == "true")
        self.exit_box.toggled.connect(self._toggle_exits)
        self.entry_box = QCheckBox(tr("Mostra ingressi"))
        saved_entries = QSettings("enkas79", "BTC_Cycle").value("chart_entries", "true")
        self.entry_box.setChecked(str(saved_entries) == "true")
        self.entry_box.toggled.connect(self._toggle_entries)
        self.view_box = QComboBox()
        self.view_box.addItem(tr("Prezzo e livelli"), "price")
        self.view_box.addItem(tr("Cicli sovrapposti"), "cycles")
        self.view_box.currentIndexChanged.connect(self._view_changed)
        save = QPushButton(tr("Esporta immagine…"))
        save.clicked.connect(self.export_image)
        copy = QPushButton(tr("Copia"))
        copy.clicked.connect(self.copy_image)
        top = QHBoxLayout()
        top.addWidget(self.view_box)
        for w in (self.log_box, self.entry_box, self.exit_box):
            top.addWidget(w)
        top.addStretch(1)
        for w in (reset, refresh, save, copy):
            top.addWidget(w)
        # L'immagine esportata è solo la "tela": stato, grafico e fonti, senza i pulsanti
        self.canvas = QWidget()
        self.canvas.setAutoFillBackground(True)
        self.canvas.setStyleSheet("background: #ffffff;")
        inner = QVBoxLayout(self.canvas)
        inner.addWidget(self.info)
        inner.addWidget(self.stack, 1)
        inner.addWidget(self.sources)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.canvas, 1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(POLL_MS)

    # ------------------------------------------------------------------ dati
    def set_plan(self, plan: Plan) -> None:
        self.plan = plan
        self.sources.setText(tr("Fonti: {docs}. Livelli e finestre sono stime di terzi, non previsioni.")
                             .format(docs="; ".join(plan.documents)))
        self._redraw(reset_view=True)
        if not self.history:
            self.load_history()

    def load_history(self) -> None:
        if self._busy:
            return
        self._busy = True
        self._status = tr("Download storico…")
        self._update_info()

        def done(rows) -> None:
            self._busy = False
            self.history = rows
            self.spot = rows[-1][1] if rows else self.spot
            self._status = tr("storico aggiornato {t}").format(t=f"{datetime.now():%H:%M:%S}")
            self._redraw(reset_view=True)

        self._run(fetch_history, ok=done, fail=self._failed)

    def _tick(self) -> None:
        if self._busy or not self.isVisible() or not self.history:
            return
        self._busy = True

        def done(price: float) -> None:
            self._busy = False
            self.spot = price
            self._status = tr("live {t}").format(t=f"{datetime.now():%H:%M:%S}")
            self._redraw(reset_view=False)

        self._run(fetch_spot, ok=done, fail=self._failed)

    def _failed(self, err: str) -> None:
        self._busy = False
        self._status = tr("errore di rete ({err})").format(err=err)
        self._update_info()

    # --------------------------------------------------------------- disegno
    def _update_info(self) -> None:
        if not self.spot:
            self.info.setText(self._status or tr("In attesa dei dati di mercato…"))
            return
        parts = [f"<b>BTC {usd(self.spot)}</b>"]
        if self.plan:
            near = nearest_zone(self.plan, self.spot)
            if near:
                parts.append(tr("dentro la ladder {n}").format(n=near[0]) if near[1] == 0 else
                             tr("gradino {n} della ladder: {d:+.1f}%").format(n=near[0], d=near[1]))
        rally = rally_from_low([c for _, c in self.history], self.spot)
        if rally:
            parts.append(tr("rally dal minimo {low}: {pct:+.0f}% (mediana rally falliti +{med:.0f}%, "
                            "15 casi, solo contesto)").format(low=usd(rally[0]), pct=rally[1],
                                                              med=FAILED_RALLY_MEDIAN_PCT))
        parts.append(self._status)
        self.info.setText(" · ".join(p for p in parts if p))

    def _on_click(self, ev) -> None:
        """Click sinistro: linee di prezzo e data nel punto; click destro: le rimuove."""
        vb = self.plot.getPlotItem().vb
        if not self.history or not vb.sceneBoundingRect().contains(ev.scenePos()):
            return
        if ev.button() == pg.QtCore.Qt.MouseButton.RightButton:
            self._click = None
        elif ev.button() == pg.QtCore.Qt.MouseButton.LeftButton:
            pt = vb.mapSceneToView(ev.scenePos())
            price = 10 ** pt.y() if self.log_box.isChecked() else pt.y()
            self._click = (pt.x(), price) if price > 0 else None
        else:
            return
        self._redraw(reset_view=False)

    def _draw_exits(self, ov, ymax: float) -> None:
        red = "#b71c1c"
        for w in ov.exits:
            if w.kind == "peak":
                self.plot.addItem(pg.LinearRegionItem((_ts(w.start), _ts(w.end)), orientation="vertical",
                                                      movable=False, brush=pg.mkBrush("#c6282826"),
                                                      pen=_pen(red)), ignoreBounds=True)
                self._label(w.label, _ts(w.start), ymax * 0.78, red)
            else:
                self.plot.addItem(pg.InfiniteLine(_ts(w.start), angle=90, pen=_pen(red, 2, True)),
                                  ignoreBounds=True)
                self._label(w.label, _ts(w.start), ymax * 0.45, red, angle=90)
        for lv in ov.exit_levels:
            self.plot.addItem(pg.InfiniteLine(self._y(lv.high), angle=0, pen=_pen(red, 1, True)),
                              ignoreBounds=True)
            self._label(lv.label, self.plot.getPlotItem().vb.viewRange()[0][1], lv.high, red, right=True)

    def _draw_click(self) -> None:
        x, price = self._click
        pen = _pen("#6a1b9a", 1, dash=True)
        self.plot.addItem(pg.InfiniteLine(self._y(price), angle=0, pen=pen), ignoreBounds=True)
        self.plot.addItem(pg.InfiniteLine(x, angle=90, pen=pen), ignoreBounds=True)
        text = f"{fmt_date(datetime.fromtimestamp(x).date())} · {usd(price)}"
        if self.spot:
            text += " " + tr("({d:+.1f}% dal prezzo attuale)").format(d=(price / self.spot - 1) * 100)
        x_min, x_max = self.plot.getPlotItem().vb.viewRange()[0]
        self._label(text, x, price, "#6a1b9a", right=x > (x_min + x_max) / 2)

    def set_full_history(self, rows: List[Tuple[float, float]]) -> None:
        self.full_history = rows
        if self.view_box.currentData() == "cycles":
            self._redraw(reset_view=True)

    def _toggle_entries(self, checked: bool) -> None:
        QSettings("enkas79", "BTC_Cycle").setValue("chart_entries", checked)
        self._redraw(reset_view=True)

    def _view_changed(self) -> None:
        cycles = self.view_box.currentData() == "cycles"
        self.stack.setCurrentWidget(self.cycle_plot if cycles else self.plot)
        for w in (self.log_box, self.entry_box, self.exit_box):
            w.setEnabled(not cycles)
        self._redraw(reset_view=True)

    def _draw_cycles(self) -> None:
        """Cicli a confronto: prezzo / prezzo all'halving (scala log) per giorni dall'halving."""
        plot = self.cycle_plot
        plot.clear()
        if plot.plotItem.legend is not None:
            plot.plotItem.legend.clear()
        else:
            plot.addLegend(offset=(10, 10))
        plot.setLogMode(x=False, y=True)
        series = cycle_series(self.full_history)
        if not series:
            self.info.setText(tr("Storico completo non ancora disponibile."))
            return
        self.info.setText(tr("Prezzo normalizzato al giorno dell'halving (=1). I cicli passati non "
                             "garantiscono quello attuale: 4 campioni, rendimenti decrescenti."))
        colors = ["#6b7280", "#1565c0", "#6a1b9a"]
        last = max(series)
        for i, (h, rows) in enumerate(sorted(series.items())):
            current = h == last
            pen = _pen("#f7931a", 3) if current else _pen(colors[i % len(colors)], 2)
            name = tr("Ciclo {y}").format(y=h.year) + (" · " + tr("in corso") if current else "")
            plot.addItem(pg.PlotDataItem([r[0] for r in rows], [r[1] for r in rows], pen=pen, name=name))
        if self.plan:
            s = self.plan.situation
            for key, label in (("est_peak", tr("Picco stimato")), ("est_bottom", tr("Minimo stimato"))):
                if s.get(key) and s.get("last_halving"):
                    x = (s[key] - s["last_halving"]).days
                    opts = {"position": 0.95, "color": ACCENT_DARK}
                    plot.addItem(pg.InfiniteLine(x, angle=90, pen=_pen(ACCENT_DARK, 1, True),
                                                 label=label, labelOpts=opts))
        plot.enableAutoRange()

    def _toggle_exits(self, checked: bool) -> None:
        QSettings("enkas79", "BTC_Cycle").setValue("chart_exits", checked)
        self._redraw(reset_view=True)

    def export_image(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, tr("Esporta immagine…"),
                                              f"btc_chart_{date.today():%Y%m%d}.png", "PNG (*.png)")
        if path and not self.canvas.grab().save(path, "PNG"):
            QMessageBox.warning(self, tr("Esporta"), tr("Impossibile salvare: {e}").format(e=path))

    def copy_image(self) -> None:
        QApplication.clipboard().setPixmap(self.canvas.grab())
        self.info.setToolTip(tr("Grafico copiato negli appunti."))

    def _y(self, v: float) -> float:
        """Le posizioni degli oggetti del grafico sono in log10 quando la scala è logaritmica."""
        return math.log10(v) if self.log_box.isChecked() else v

    def _toggle_log(self, checked: bool) -> None:
        QSettings("enkas79", "BTC_Cycle").setValue("chart_log", checked)
        self._redraw(reset_view=True)

    def _label(self, text: str, x: float, y: float, color: str, right: bool = False,
               angle: float = 0) -> None:
        item = pg.TextItem(text, color=color, anchor=(1 if right else 0, 1), angle=angle)
        item.setPos(x, self._y(y))
        self.plot.addItem(item, ignoreBounds=True)

    def _redraw(self, reset_view: bool) -> None:
        if self.view_box.currentData() == "cycles":
            self._draw_cycles()
            return
        self._update_info()
        if not self.history:
            return
        plot = self.plot
        plot.clear()
        plot.setLogMode(x=False, y=self.log_box.isChecked())
        xs, ys = [h[0] for h in self.history], [h[1] for h in self.history]
        today = date.today()
        show_exits = bool(self.plan and self.plan.exit_steps and self.exit_box.isChecked())
        end_date = today + timedelta(days=FUTURE_DAYS)
        if show_exits:
            end_date = max(end_date, max(x["date"] for x in self.plan.exit_steps) + timedelta(days=90))
        x_end = _ts(end_date)
        x0 = xs[0]
        plot.addItem(pg.PlotDataItem(xs, ys, pen=_pen(INK, 2)), ignoreBounds=True)
        lows = list(ys)
        highs = list(ys)

        if self.plan:
            ov = build_overlays(self.plan, datetime.fromtimestamp(x0).date(), end_date)
            now_pt = min(range(len(ov.fair_curve)), key=lambda i: abs(ov.fair_curve[i][0] - today),
                         default=None) if ov.fair_curve else None
            if now_pt is not None:  # la vista deve contenere fair value e floor di oggi
                highs.append(ov.fair_curve[now_pt][1])
                lows.append(ov.floor_curve[now_pt][1])
            lows += [lv.low for lv in ov.levels if lv.low > 0]
            highs += [lv.high for lv in ov.levels]
            if show_exits:
                highs += [lv.high for lv in ov.exit_levels]
            ymin, ymax = min(lows) * 0.85, max(highs) * 1.1
            for name, curve, color in ((tr("Fair value power law"), ov.fair_curve, LEVEL_COLORS["fair"]),
                                       (tr("Floor power law"), ov.floor_curve, LEVEL_COLORS["floor"])):
                if curve:
                    plot.addItem(pg.PlotDataItem([_ts(d) for d, _ in curve], [v for _, v in curve],
                                                 pen=_pen(color, 1, dash=True)), ignoreBounds=True)
                    i = min(len(curve) - 1, now_pt + 8)
                    self._label(name, _ts(curve[i][0]), curve[i][1], color)
            for w in ov.windows:
                brush = pg.mkBrush(QColor(ACCENT_DARK).lighter(170).name() + "40")
                if w.start == w.end:
                    plot.addItem(pg.InfiniteLine(_ts(w.start), angle=90, pen=_pen(ACCENT_DARK, 1, True)),
                                 ignoreBounds=True)
                else:
                    plot.addItem(pg.LinearRegionItem((_ts(w.start), _ts(w.end)), orientation="vertical",
                                                     movable=False, brush=brush, pen=_pen(ACCENT_DARK)),
                                 ignoreBounds=True)
                self._label(w.label, _ts(w.start), ymax * (0.82 if w.kind == "bottom" else 0.9), ACCENT_DARK)
            floor_y = ymin
            if show_exits:
                self._draw_exits(ov, ymax)
            for lv in ov.levels:
                if lv.kind == "ladder":
                    if not self.entry_box.isChecked():
                        continue
                    lo = lv.low if lv.low > 0 else floor_y
                    plot.addItem(pg.LinearRegionItem((self._y(lo), self._y(lv.high)),
                                                     orientation="horizontal", movable=False,
                                                     brush=pg.mkBrush("#2e7d3233"), pen=_pen("#2e7d32")),
                                 ignoreBounds=True)
                    self._label(lv.label, x0, lv.high, "#1b5e20")
                else:
                    color = LEVEL_COLORS.get(lv.kind, INK)
                    plot.addItem(pg.InfiniteLine(self._y(lv.high), angle=0, pen=_pen(color, 1, True)),
                                 ignoreBounds=True)
                    self._label(lv.label, x0, lv.high, color)

        if self.spot:
            plot.addItem(pg.InfiniteLine(self._y(self.spot), angle=0, pen=_pen("#f7931a", 2)),
                         ignoreBounds=True)
            self._label(tr("Prezzo {p}").format(p=usd(self.spot)), xs[-1], self.spot, ACCENT_DARK)

        if self._click:
            self._draw_click()

        if reset_view:
            ymin, ymax = min(lows) * 0.85, max(highs) * 1.1
            plot.setXRange(x0, x_end if self.plan else xs[-1] + 30 * 86400, padding=0)
            plot.setYRange(self._y(ymin), self._y(ymax), padding=0)
