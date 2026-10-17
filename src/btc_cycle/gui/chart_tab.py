"""Scheda grafico: prezzo BTC con i livelli e le finestre della strategia."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Callable, List, Optional, Tuple

import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ..core.chart import FAILED_RALLY_MEDIAN_PCT, build_overlays, nearest_zone, rally_from_low
from ..core.market import fetch_history, fetch_spot
from ..core.planner import Plan, usd
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
        self.spot: Optional[float] = None
        self._busy = False
        self._status = ""

        pg.setConfigOptions(antialias=True, background="w", foreground=INK)
        self.plot = pg.PlotWidget(axisItems={"bottom": pg.DateAxisItem()})
        self.plot.showGrid(x=True, y=True, alpha=0.15)
        self.plot.setMenuEnabled(False)
        self.plot.getAxis("left").setLabel("USD")

        self.info = QLabel("Genera un piano per vedere livelli e finestre della strategia.")
        self.info.setObjectName("hint")
        self.info.setWordWrap(True)
        self.sources = QLabel()
        self.sources.setObjectName("hint")
        self.sources.setWordWrap(True)
        refresh = QPushButton("Aggiorna storico")
        refresh.clicked.connect(self.load_history)
        reset = QPushButton("Reimposta vista")
        reset.clicked.connect(lambda: self._redraw(reset_view=True))

        top = QHBoxLayout()
        top.addWidget(self.info, 1)
        top.addWidget(reset)
        top.addWidget(refresh)
        layout = QVBoxLayout(self)
        layout.addLayout(top)
        layout.addWidget(self.plot, 1)
        layout.addWidget(self.sources)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(POLL_MS)

    # ------------------------------------------------------------------ dati
    def set_plan(self, plan: Plan) -> None:
        self.plan = plan
        self.sources.setText("Fonti: " + "; ".join(plan.documents) +
                             ". Livelli e finestre sono stime di terzi, non previsioni.")
        self._redraw(reset_view=True)
        if not self.history:
            self.load_history()

    def load_history(self) -> None:
        if self._busy:
            return
        self._busy = True
        self._status = "Download storico…"
        self._update_info()

        def done(rows) -> None:
            self._busy = False
            self.history = rows
            self.spot = rows[-1][1] if rows else self.spot
            self._status = f"storico aggiornato {datetime.now():%H:%M:%S}"
            self._redraw(reset_view=True)

        self._run(fetch_history, ok=done, fail=self._failed)

    def _tick(self) -> None:
        if self._busy or not self.isVisible() or not self.history:
            return
        self._busy = True

        def done(price: float) -> None:
            self._busy = False
            self.spot = price
            self._status = f"live {datetime.now():%H:%M:%S}"
            self._redraw(reset_view=False)

        self._run(fetch_spot, ok=done, fail=self._failed)

    def _failed(self, err: str) -> None:
        self._busy = False
        self._status = f"errore di rete ({err})"
        self._update_info()

    # --------------------------------------------------------------- disegno
    def _update_info(self) -> None:
        if not self.spot:
            self.info.setText(self._status or "In attesa dei dati di mercato…")
            return
        parts = [f"<b>BTC {usd(self.spot)}</b>"]
        if self.plan:
            near = nearest_zone(self.plan, self.spot)
            if near:
                parts.append("dentro la ladder " + str(near[0]) if near[1] == 0 else
                             f"gradino {near[0]} della ladder: {near[1]:+.1f}%")
        rally = rally_from_low([c for _, c in self.history], self.spot)
        if rally:
            parts.append(f"rally dal minimo {usd(rally[0])}: {rally[1]:+.0f}% (mediana rally falliti "
                         f"+{FAILED_RALLY_MEDIAN_PCT:.0f}%, 15 casi, solo contesto)")
        parts.append(self._status)
        self.info.setText(" · ".join(p for p in parts if p))

    def _label(self, text: str, x: float, y: float, color: str) -> None:
        item = pg.TextItem(text, color=color, anchor=(0, 1))
        item.setPos(x, y)
        self.plot.addItem(item, ignoreBounds=True)

    def _redraw(self, reset_view: bool) -> None:
        self._update_info()
        if not self.history:
            return
        plot = self.plot
        plot.clear()
        xs, ys = [h[0] for h in self.history], [h[1] for h in self.history]
        today = date.today()
        x_end = _ts(today + timedelta(days=FUTURE_DAYS))
        x0 = xs[0]
        plot.addItem(pg.PlotDataItem(xs, ys, pen=_pen(INK, 2)), ignoreBounds=True)
        lows = list(ys)
        highs = list(ys)

        if self.plan:
            ov = build_overlays(self.plan, datetime.fromtimestamp(x0).date(),
                                today + timedelta(days=FUTURE_DAYS))
            now_pt = min(range(len(ov.fair_curve)), key=lambda i: abs(ov.fair_curve[i][0] - today),
                         default=None) if ov.fair_curve else None
            if now_pt is not None:  # la vista deve contenere fair value e floor di oggi
                highs.append(ov.fair_curve[now_pt][1])
                lows.append(ov.floor_curve[now_pt][1])
            lows += [lv.low for lv in ov.levels if lv.low > 0]
            highs += [lv.high for lv in ov.levels]
            ymin, ymax = min(lows) * 0.85, max(highs) * 1.1
            for name, curve, color in (("Fair value power law", ov.fair_curve, LEVEL_COLORS["fair"]),
                                       ("Floor power law", ov.floor_curve, LEVEL_COLORS["floor"])):
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
                self._label(w.label, _ts(w.start), ymax * 0.97, ACCENT_DARK)
            floor_y = ymin
            for lv in ov.levels:
                if lv.kind == "ladder":
                    lo = lv.low if lv.low > 0 else floor_y
                    plot.addItem(pg.LinearRegionItem((lo, lv.high), orientation="horizontal",
                                                     movable=False, brush=pg.mkBrush("#2e7d3233"),
                                                     pen=_pen("#2e7d32")), ignoreBounds=True)
                    self._label(lv.label, x0, lv.high, "#1b5e20")
                else:
                    color = LEVEL_COLORS.get(lv.kind, INK)
                    plot.addItem(pg.InfiniteLine(lv.high, angle=0, pen=_pen(color, 1, True)),
                                 ignoreBounds=True)
                    self._label(lv.label, x0, lv.high, color)

        if self.spot:
            plot.addItem(pg.InfiniteLine(self.spot, angle=0, pen=_pen("#f7931a", 2)), ignoreBounds=True)
            self._label(f"Prezzo {usd(self.spot)}", xs[-1], self.spot, ACCENT_DARK)

        if reset_view:
            ymin, ymax = min(lows) * 0.85, max(highs) * 1.1
            plot.setXRange(x0, x_end if self.plan else xs[-1] + 30 * 86400, padding=0)
            plot.setYRange(ymin, ymax, padding=0)
