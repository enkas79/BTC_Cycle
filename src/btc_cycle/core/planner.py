"""Motore del piano: combina i parametri estratti dai documenti con i dati di mercato."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from . import cycle as cy
from .knowledge import KnowledgeBase

# Valori usati quando nessun documento fornisce il parametro
DEFAULTS: Dict[str, Any] = {
    "cycle.peak_offset_months": 18,
    "cycle.bottom_offset_months": 30,
    "cycle.dca_start_offset_months": 30,
    "cycle.accumulation_offsets": [30, 48],
    "cycle.days_to_peak_range": [500, 550],
    "cycle.next_gain_range": [200, 400],
    "accum.streams": {"ladder": 50, "drip": 30, "reserve": 20},
    "accum.drip_daily_pct": 1.0,
    "accum.drip_daily_pct_slow": 0.5,
    "accum.flush_pct": 10.0,
    "accum.anti_miss_weekly_pct": 3.0,
    "dca.front_load": [
        {"from": 1, "to": 3, "pct": 40},
        {"from": 4, "to": 6, "pct": 30},
        {"from": 7, "to": 9, "pct": 20},
        {"from": 10, "to": 12, "pct": 10},
    ],
    "dca.booster_cap": 50,
    "dca.kill_switch_pct": 40,
    "exit.schedule": [
        {"offset_months": 12, "sell_pct": 25},
        {"offset_months": 15, "sell_pct": 25},
        {"offset_months": 18, "sell_pct": 25},
    ],
    "exit.moonbag_pct": 25,
}

PROFILES: Dict[str, Dict[str, float]] = {
    "prudente": {"bottom_pot": 40, "alts_max": 0, "eth_max": 0},
    "bilanciato": {"bottom_pot": 50, "alts_max": 20, "eth_max": 10},
    "aggressivo": {"bottom_pot": 60, "alts_max": 30, "eth_max": 20},
}


@dataclass
class PlanInputs:
    capital: float
    btc_price_usd: float
    currency: str = "EUR"
    usd_per_unit: float = 1.0  # USD per 1 unità della valuta del capitale
    today: date = field(default_factory=date.today)
    profile: str = "bilanciato"
    bottom_pot_pct: Optional[float] = None  # None = default del profilo
    repeg_ladder: bool = True
    slow_drip: bool = False
    fear_greed: Optional[int] = None
    ma200: Optional[float] = None
    high200: Optional[float] = None
    vix: Optional[float] = None
    cycle_low_close: Optional[float] = None


@dataclass
class Plan:
    inputs: PlanInputs
    situation: Dict[str, Any] = field(default_factory=dict)
    pots: Dict[str, float] = field(default_factory=dict)
    ladder: List[Dict[str, Any]] = field(default_factory=list)
    drip: Dict[str, Any] = field(default_factory=dict)
    reserve: Dict[str, Any] = field(default_factory=dict)
    dca: List[Dict[str, Any]] = field(default_factory=list)
    dca_notes: List[str] = field(default_factory=list)
    boosters: List[Dict[str, Any]] = field(default_factory=list)
    boost_now: Dict[str, Any] = field(default_factory=dict)
    allocation: List[str] = field(default_factory=list)
    exit_steps: List[Dict[str, Any]] = field(default_factory=list)
    exit_notes: List[str] = field(default_factory=list)
    levels: List[Dict[str, Any]] = field(default_factory=list)
    scenarios: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    bottom_estimates: List[Dict[str, Any]] = field(default_factory=list)
    actions_now: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    params_used: List[Tuple[str, str, str]] = field(default_factory=list)
    documents: List[str] = field(default_factory=list)


def usd(v: Optional[float]) -> str:
    return "n/d" if v is None else f"${v:,.0f}"


def pct(v: Optional[float], sign: bool = True) -> str:
    if v is None:
        return "n/d"
    return f"{v:+.1f}%" if sign else f"{v:.1f}%"


class Planner:
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        self.params = kb.effective_params()

    # --- accesso ai parametri con tracciamento della fonte ---
    def get(self, key: str, default: Any = None) -> Tuple[Any, str]:
        if key in self.params:
            p = self.params[key]
            return p.value, p.doc_title
        if key in DEFAULTS:
            return DEFAULTS[key], "predefinito"
        return default, ""

    def val(self, key: str, default: Any = None) -> Any:
        return self.get(key, default)[0]

    def _track(self, plan: Plan, label: str, key: str) -> None:
        value, source = self.get(key)
        if value is not None:
            plan.params_used.append((label, _short(value), source))

    # --- costruzione del piano ---
    def build(self, inp: PlanInputs) -> Plan:
        if inp.btc_price_usd <= 0 or inp.capital <= 0:
            raise ValueError("Capitale e prezzo BTC devono essere maggiori di zero.")
        plan = Plan(inputs=inp)
        plan.documents = [f"{d.title} ({self.kb.effective_date(d)}, {d.source})"
                          for d in self.kb.sorted_documents()]
        self._situation(plan)
        self._pots(plan)
        self._bottom_pot(plan)
        self._dca(plan)
        self._allocation(plan)
        self._exit(plan)
        self._levels(plan)
        self._scenarios(plan)
        self._actions(plan)
        self._warnings(plan)
        return plan

    def _next_halving_param(self) -> Optional[date]:
        iso = self.val("cycle.next_halving")
        if not iso:
            return None
        y, m = int(iso[:4]), int(iso[5:7])
        est = cy.NEXT_HALVING_ESTIMATE
        return est if (est.year, est.month) == (y, m) else date(y, m, 15)

    def _situation(self, plan: Plan) -> None:
        inp, s = plan.inputs, plan.situation
        today, price = inp.today, inp.btc_price_usd
        nh = self._next_halving_param()
        lh = cy.last_halving(today, nh)
        m_since = cy.months_between(lh, today)
        peak_off = int(self.val("cycle.peak_offset_months"))
        bottom_off = int(self.val("cycle.bottom_offset_months"))
        acc = self.val("cycle.accumulation_offsets")
        phase = cy.cycle_phase(m_since, peak_off, bottom_off, int(acc[1]))
        for label, key in [("Picco (mesi post-halving)", "cycle.peak_offset_months"),
                           ("Minimo (mesi post-halving)", "cycle.bottom_offset_months"),
                           ("Accumulo (mesi post-halving)", "cycle.accumulation_offsets")]:
            self._track(plan, label, key)

        s.update(today=today, price=price, last_halving=lh, months_since=m_since,
                 days_since=(today - lh).days, phase=phase,
                 next_halving=cy.next_halving_after(today, nh),
                 est_peak=cy.add_months(lh, peak_off), est_bottom=cy.add_months(lh, bottom_off),
                 accumulation_start=cy.add_months(lh, acc[0]),
                 accumulation_end=cy.add_months(lh, acc[1]))

        # Finestra di minimo: dal documento se presente, altrimenti H+bottom±3 mesi
        window = self.val("accum.window")
        w_start, w_end = cy.add_months(lh, bottom_off - 3), cy.add_months(lh, bottom_off + 3)
        if window:
            ys, ms = int(window["start"][:4]), int(window["start"][5:7])
            ye, me = int(window["end"][:4]), int(window["end"][5:7])
            d_start = date(ys, ms, 1)
            d_end = cy.add_months(date(ye, me, 1), 1) - timedelta(days=1)
            if d_end > lh:  # stesso ciclo
                w_start, w_end = d_start, d_end
                self._track(plan, "Finestra di accumulo", "accum.window")
        s["window_start"], s["window_end"] = w_start, w_end

        ath = self.val("cycle.ath")
        if ath:
            self._track(plan, "Massimo di ciclo", "cycle.ath")
            s["ath"] = ath["price"]
            s["ath_date"] = date.fromisoformat(ath["date"]) if ath.get("date") else None
            s["drawdown"] = (price / ath["price"] - 1) * 100
            ttl = self.val("cycle.top_to_low_months")
            if ttl and s["ath_date"]:
                self._track(plan, "Mesi massimo→minimo", "cycle.top_to_low_months")
                s["ttl_window"] = (cy.add_months(s["ath_date"], min(ttl)),
                                   cy.add_months(s["ath_date"], max(ttl)))

        # Power law calibrata sui documenti
        pl = cy.PowerLaw()
        exp = self.val("power_law.exponent")
        if exp:
            pl.exponent = float(exp)
        anchor = self.val("power_law.anchor")
        if anchor and anchor.get("date"):
            pl.calibrate_fair(anchor["price"], anchor["pct_below"], date.fromisoformat(anchor["date"]))
            self._track(plan, "Ancora fair value power law", "power_law.anchor")
        floor = self.val("power_law.floor")
        if floor and floor.get("date"):
            mid = (floor["low"] + floor["high"]) / 2
            pl.calibrate_floor(mid, date.fromisoformat(floor["date"]))
            self._track(plan, "Floor power law", "power_law.floor")
        s["power_law"] = pl
        s["fair"], s["floor"] = pl.fair_value(today), pl.floor(today)
        s["vs_fair"] = (price / s["fair"] - 1) * 100
        s["vs_floor"] = (price / s["floor"] - 1) * 100

    def _pots(self, plan: Plan) -> None:
        inp, s = plan.inputs, plan.situation
        profile = PROFILES.get(inp.profile, PROFILES["bilanciato"])
        bottom_pct = inp.bottom_pot_pct if inp.bottom_pot_pct is not None else profile["bottom_pot"]
        phase = s["phase"].key
        deploy = phase in ("bear", "bottom", "accumulation")
        if phase in ("bull", "peak"):
            plan.dca_notes.append(
                "Fase di rialzo/picco: i documenti non prevedono nuovi acquisti ora. Il capitale "
                "resta non allocato fino alla prossima finestra di minimo."
            )
        window_open = inp.today <= s["window_end"]
        if not window_open or phase == "accumulation":
            bottom_pct = 0.0
        if not deploy:
            bottom_pct = 0.0
        plan.pots = {
            "capital": inp.capital,
            "bottom_pct": bottom_pct,
            "bottom": inp.capital * bottom_pct / 100 if deploy else 0.0,
            "dca": inp.capital * (100 - bottom_pct) / 100 if deploy else 0.0,
            "idle": 0.0 if deploy else inp.capital,
        }

    def _btc(self, plan: Plan, amount: float, price_usd: float) -> float:
        return amount * plan.inputs.usd_per_unit / price_usd if price_usd > 0 else 0.0

    def _bottom_pot(self, plan: Plan) -> None:
        inp, s = plan.inputs, plan.situation
        pot = plan.pots["bottom"]
        streams = self.val("accum.streams")
        self._track(plan, "Flussi ladder/drip/riserva", "accum.streams")
        flush_pct = float(self.val("accum.flush_pct"))
        reserve_total = pot * streams.get("reserve", 20) / 100
        flush_amount = min(reserve_total, pot * flush_pct / 100)
        backstop = reserve_total - flush_amount
        price = inp.btc_price_usd

        zones = self.val("accum.ladder")
        factor = 1.0
        if zones:
            self._track(plan, "Zone ladder", "accum.ladder")
            floor = self.val("power_law.floor")
            if inp.repeg_ladder and floor:
                ref = (floor["low"] + floor["high"]) / 2
                factor = s["floor"] / ref
        else:
            # Senza documenti: zone in % sotto il floor attuale
            f = s["floor"]
            zones = [
                {"low": f * 0.95, "high": f * 1.0, "pct": 10, "plus_reserve": False},
                {"low": f * 0.87, "high": f * 0.95, "pct": 13, "plus_reserve": False},
                {"low": f * 0.78, "high": f * 0.87, "pct": 16, "plus_reserve": False},
                {"low": 0.0, "high": f * 0.78, "pct": 11, "plus_reserve": True},
            ]
        s["ladder_factor"] = factor
        low_close = inp.cycle_low_close
        for i, z in enumerate(zones, start=1):
            lo, hi = z["low"] * factor, z["high"] * factor
            amount = pot * z["pct"] / 100 + (flush_amount if z.get("plus_reserve") else 0.0)
            ref_price = (lo + hi) / 2 if lo > 0 else hi * 0.95
            trigger = min(hi, low_close) if low_close else hi
            if lo > 0 and lo <= price <= hi:
                status = "IN ZONA ora"
            elif price < (lo if lo > 0 else hi):
                status = "sotto la zona (acquistabile)"
            else:
                status = f"in attesa ({(trigger / price - 1) * 100:+.1f}% dal prezzo)"
            plan.ladder.append({
                "rung": i, "low": lo, "high": hi, "pct": z["pct"],
                "plus_reserve": z.get("plus_reserve", False), "amount": amount,
                "btc": self._btc(plan, amount, ref_price), "trigger": trigger, "status": status,
            })

        drip_pct = float(self.val("accum.drip_daily_pct_slow" if inp.slow_drip
                                  else "accum.drip_daily_pct"))
        self._track(plan, "Drip giornaliero %", "accum.drip_daily_pct")
        drip_total = pot * streams.get("drip", 30) / 100
        daily = pot * drip_pct / 100
        plan.drip = {
            "pct": drip_pct, "daily": daily, "total": drip_total,
            "days": int(drip_total / daily) if daily else 0,
            "active": price < s["floor"], "floor": s["floor"],
        }

        weeks_pct = float(self.val("accum.anti_miss_weekly_pct"))
        trigger_date = s["window_end"] - timedelta(weeks=4)
        weeks_left = max(1, (s["window_end"] - max(inp.today, trigger_date)).days // 7)
        plan.reserve = {
            "total": reserve_total, "flush": flush_amount, "backstop": backstop,
            "anti_miss_date": trigger_date, "window_end": s["window_end"],
            "anti_miss_active": inp.today >= trigger_date and pot > 0,
            "weekly_min": pot * weeks_pct / 100, "weeks_left": weeks_left,
            "weekly_all_residual": pot / weeks_left if pot else 0.0,
        }

    def _dca(self, plan: Plan) -> None:
        inp, s = plan.inputs, plan.situation
        pot = plan.pots["dca"]
        blocks = self.val("dca.front_load")
        self._track(plan, "DCA front-loaded", "dca.front_load")
        start = max(inp.today, cy.add_months(s["last_halving"],
                                              self.val("cycle.dca_start_offset_months")))
        s["dca_start"] = start
        cap = float(self.val("dca.booster_cap"))
        n_months = max(b["to"] for b in blocks)
        for month in range(1, n_months + 1):
            block = next((b for b in blocks if b["from"] <= month <= b["to"]), None)
            share = block["pct"] / (block["to"] - block["from"] + 1) if block else 0.0
            amount = pot * share / 100
            plan.dca.append({"n": month, "date": cy.add_months(start, month - 1), "pct": share,
                             "amount": amount, "max_amount": amount * (1 + cap / 100)})
        if pot and inp.today > s["accumulation_end"]:
            plan.dca_notes.append("La finestra di accumulo primaria (H+48) è già chiusa.")
        plan.dca_notes.append(
            "I boost si finanziano anticipando le rate finali (il piano si accorcia), "
            "non aggiungendo capitale nuovo."
        )

        price = inp.btc_price_usd
        defs = [
            ("dca.booster_drawdown", "BTC ≥{t}% sotto il massimo a 200 giorni",
             None if not inp.high200 else (lambda t: price <= inp.high200 * (1 - t / 100))),
            ("dca.booster_fear", "Fear & Greed sotto {t}",
             None if inp.fear_greed is None else (lambda t: inp.fear_greed < t)),
            ("dca.booster_vix", "VIX sopra {t} (o picco di volatilità crypto)",
             None if inp.vix is None else (lambda t: inp.vix > t)),
        ]
        total = 0.0
        for key, text, check in defs:
            rule = self.val(key)
            if not rule:
                continue
            self._track(plan, "Boost: " + text.format(t=rule["threshold"]), key)
            active = None if check is None else bool(check(rule["threshold"]))
            if active:
                total += rule["boost"]
            plan.boosters.append({"condition": text.format(t=rule["threshold"]),
                                  "boost": rule["boost"], "active": active})
        kill_pct = float(self.val("dca.kill_switch_pct"))
        kill = None if not inp.ma200 else price > inp.ma200 * (1 + kill_pct / 100)
        plan.boost_now = {
            "total": 0.0 if kill else min(total, cap), "cap": cap, "kill_switch": kill,
            "kill_pct": kill_pct, "ma200": inp.ma200,
        }

    def _allocation(self, plan: Plan) -> None:
        profile = PROFILES.get(plan.inputs.profile, PROFILES["bilanciato"])
        init = self.val("alloc.initial") or {"months": 6, "btc_pct": 100, "eth_max_pct": 20}
        alts = self.val("alloc.alts") or {"from_month": 6, "to_month": 12, "min_pct": 20,
                                          "max_pct": 30, "top": 25}
        eth = min(profile["eth_max"], init["eth_max_pct"])
        alt_max = min(profile["alts_max"], alts["max_pct"])
        plan.allocation.append(
            f"Primi {init['months']} mesi: {100 - eth:.0f}% BTC"
            + (f", fino a {eth:.0f}% ETH." if eth else " (profilo: niente ETH).")
        )
        if alt_max:
            plan.allocation.append(
                f"Mesi {alts['from_month']}–{alts['to_month']}: fino a {alt_max:.0f}% in altcoin "
                f"top-{alts['top']}, solo con trend settimanale di BTC al rialzo. "
                "Evitare ranking 51–100 (nei dati dei documenti: rendimenti negativi e molti fallimenti)."
            )
        else:
            plan.allocation.append("Profilo prudente: 100% BTC, nessuna altcoin.")
        if self.val("rule.no_leverage", True):
            plan.allocation.append("Nessuna leva finanziaria.")

    def _exit(self, plan: Plan) -> None:
        s = plan.situation
        nh = s["next_halving"]
        steps = self.val("exit.schedule")
        self._track(plan, "Vendite programmate", "exit.schedule")
        remaining = 100.0
        for st in steps:
            remaining -= st["sell_pct"]
            plan.exit_steps.append({"date": cy.add_months(nh, st["offset_months"]),
                                    "offset": st["offset_months"], "sell_pct": st["sell_pct"],
                                    "remaining": remaining})
        moon = self.val("exit.moonbag_pct")
        days = self.val("cycle.days_to_peak_range")
        s["peak_window"] = (nh + timedelta(days=days[0]), nh + timedelta(days=days[1]))
        plan.exit_notes.append(
            f"Finestra di picco attesa: {s['peak_window'][0]:%b %Y} – {s['peak_window'][1]:%b %Y} "
            f"(halving {nh:%b %Y} + {days[0]}–{days[1]} giorni)."
        )
        plan.exit_notes.append(f"Quota da non vendere mai (moon bag): {moon}%.")
        rsi = self.val("exit.weekly_rsi_above")
        euph = self.val("exit.euphoria_min")
        if rsi:
            plan.exit_notes.append(f"Conferma secondaria: RSI settimanale sopra {rsi}.")
        if euph:
            plan.exit_notes.append(
                f"Vendi senza esitare se compaiono {euph}+ segnali di euforia nella finestra temporale."
            )
        plan.exit_notes.append("Nuovo massimo storico → inizia subito le prese di profitto parziali.")

    def _levels(self, plan: Plan) -> None:
        price = plan.inputs.btc_price_usd
        up = self.val("levels.invalidation_up")
        down = self.val("levels.invalidation_down")
        if up:
            self._track(plan, "Livello rialzista", "levels.invalidation_up")
            plan.levels.append({
                "name": up["name"], "price": up["price"], "kind": "rialzo",
                "status": "ROTTO: trend ribassista finito → DCA semplice" if price > up["price"]
                else f"{(up['price'] / price - 1) * 100:+.1f}% dal prezzo",
            })
        if down:
            self._track(plan, "Livello ribassista", "levels.invalidation_down")
            plan.levels.append({
                "name": down["name"], "price": down["price"], "kind": "ribasso",
                "status": "ROTTO: gamba finale ribassista → ladder" if price < down["price"]
                else f"{(down['price'] / price - 1) * 100:+.1f}% dal prezzo",
            })

    def _scenarios(self, plan: Plan) -> None:
        s = plan.situation
        bottoms = self.val("cycle.bottom_scenarios") or []
        if not bottoms and s.get("ath"):
            hist = self.val("cycle.drawdown_history") or [93, 86, 84, 77]
            for name, dd in (("Conservativo", hist[-1] - 17), ("Base", hist[-1] - 10),
                             ("Aggressivo", hist[-1] - 5)):
                bottoms.append({"name": name, "drawdown": dd, "price": s["ath"] * (1 - dd / 100)})
        plan.scenarios["bottom"] = bottoms
        gains = self.val("cycle.next_gain_range")
        peaks = []
        for b in bottoms:
            for g in range(int(gains[0]), int(gains[1]) + 1, 100):
                peaks.append({"bottom_name": b["name"], "bottom": b["price"], "gain": g,
                              "peak": b["price"] * (1 + g / 100)})
        plan.scenarios["peak"] = peaks
        plan.scenarios["target"] = [{"price": self.val("cycle.peak_target")}] if self.val(
            "cycle.peak_target") else []
        plan.bottom_estimates = self.kb.bottom_estimates()

    def _actions(self, plan: Plan) -> None:
        inp, s, a = plan.inputs, plan.situation, plan.actions_now
        cur = inp.currency
        phase = s["phase"].key
        if plan.pots["idle"]:
            a.append("Nessun acquisto: fase di rialzo/picco. Segui il piano di uscita.")
            return
        up = next((lv for lv in plan.levels if lv["kind"] == "rialzo"), None)
        if up and inp.btc_price_usd > up["price"]:
            a.append("Livello rialzista rotto: sospendi la ladder e passa a DCA semplice "
                     "(regola 'shift to plain DCA').")
        if plan.pots["bottom"]:
            active = [r for r in plan.ladder if not r["status"].startswith("in attesa")]
            for r in active:
                a.append(f"Ladder gradino {r['rung']}: acquista {r['amount']:,.0f} {cur} alla "
                         f"prossima chiusura giornaliera ≤ {usd(r['trigger'])} (nuovo minimo).")
            if plan.drip["active"]:
                a.append(f"Drip ATTIVO (prezzo sotto il floor {usd(plan.drip['floor'])}): "
                         f"{plan.drip['daily']:,.0f} {cur} al giorno.")
            else:
                a.append(f"Drip in pausa: il prezzo è sopra il floor {usd(plan.drip['floor'])}.")
            if not active:
                nxt = plan.ladder[0] if plan.ladder else None
                if nxt:
                    a.append(f"Nessun gradino attivo: il primo scatta a chiusura ≤ "
                             f"{usd(nxt['trigger'])}. Non inseguire i rally.")
            r = plan.reserve
            if r["anti_miss_active"]:
                a.append(f"Anti-miss ATTIVO: se sei investito meno del previsto, distribuisci il "
                         f"residuo del capitale 'minimo' in ~{r['weeks_left']} rate settimanali "
                         f"entro {r['window_end']:%d/%m/%Y}.")
            else:
                a.append(f"Promemoria anti-miss: dal {r['anti_miss_date']:%d/%m/%Y} valuta il "
                         f"capitale non investito.")
        if plan.pots["dca"] and plan.dca:
            first = plan.dca[0]
            boost = plan.boost_now["total"]
            a.append(f"DCA: prima rata {first['amount'] * (1 + boost / 100):,.0f} {cur} il "
                     f"{first['date']:%d/%m/%Y}" + (f" (boost +{boost:.0f}%)" if boost else "")
                     + ", poi mensile secondo il calendario.")
        if phase == "bear":
            a.append("Fase ribassista prima della finestra: preserva il capitale e prepara gli ordini.")

    def _warnings(self, plan: Plan) -> None:
        w, s, inp = plan.warnings, plan.situation, plan.inputs
        docs = self.kb.sorted_documents()
        groups = self.kb.sources()
        if len(docs) >= 2 and len(groups) == 1:
            w.append(
                f"Tutti i {len(docs)} documenti provengono dalla stessa fonte "
                f"({docs[0].source}): nessuna verifica indipendente, rischio di bias di conferma. "
                "Aggiungi analisi di autori diversi, idealmente con tesi contrarie."
            )
        promo = [d.title for d in docs if any(f.startswith("promozionale") for f in d.flags)]
        if promo:
            w.append(
                "Documenti con finalità promozionale (portano a canali a pagamento): "
                + ", ".join(promo) + ". I track record citati sono auto-dichiarati."
            )
        ests = plan.bottom_estimates
        if len(ests) >= 2:
            lo = min(ests, key=lambda e: e["low"])
            hi = max(ests, key=lambda e: e["high"])
            if hi["high"] / max(lo["low"], 1) > 1.3:
                w.append(
                    f"Le stime del minimo divergono: da {usd(lo['low'])} ({lo['doc_title']}) a "
                    f"{usd(hi['high'])} ({hi['doc_title']}). Il piano non dipende da un singolo "
                    "numero, ma la dispersione indica incertezza reale."
                )
        rng = self.val("cycle.bottom_range")
        if rng and rng["high"] < s["floor"] * 0.9:
            w.append(
                f"Incoerenza tra modelli: il range di minimo {usd(rng['low'])}–{usd(rng['high'])} "
                f"implica una rottura del floor power law ({usd(s['floor'])}) di oltre "
                f"{(1 - rng['high'] / s['floor']) * 100:.0f}%. Uno dei due modelli è sbagliato."
            )
        if "cycle.peak_offset_months" in self.params or plan.pots["dca"]:
            w.append(
                "Il 'ciclo di 4 anni' si basa su 4 osservazioni (2012, 2016, 2020, 2024): "
                "un campione minimo. ETF e istituzionali possono alterarne tempi e ampiezza."
            )
        if self.val("accum.window"):
            w.append(
                "La data del minimo attesa (ott-nov) è la più osservata dal mercato: lo stesso "
                "documento avverte che può essere anticipata dagli operatori (front-running)."
            )
        breaches = self.val("power_law.floor_breaches")
        worst = None
        if breaches:
            worst = s["floor"] * (1 - max(breaches) / 100)
            w.append(
                f"Il floor power law non è un supporto garantito: in passato è stato rotto fino al "
                f"{max(breaches):.0f}%. Oggi equivarrebbe a circa {usd(worst)}."
            )
        # Stress test sul prezzo medio d'acquisto stimato della ladder
        spent = [(r["amount"], (r["low"] + r["high"]) / 2 if r["low"] else r["high"] * 0.95)
                 for r in plan.ladder]
        tot = sum(x for x, _ in spent)
        if tot and worst:
            avg = tot / sum(x / p for x, p in spent)
            loss = (worst / avg - 1) * 100
            w.append(
                f"Stress test: prezzo medio stimato della ladder {usd(avg)}; con BTC a {usd(worst)} "
                f"la posizione segnerebbe {loss:.0f}%. Assicurati di poterlo sostenere per anni."
            )
        hist = self.val("cycle.return_history")
        if hist:
            w.append(
                "Rendimenti decrescenti ciclo dopo ciclo ("
                + " → ".join(f"{h:,}%" for h in hist)
                + "): proiettare il passato sul futuro è un'ipotesi, non un fatto."
            )
        if None in (inp.fear_greed, inp.high200, inp.ma200):
            w.append("Dati di mercato incompleti: alcuni boost/kill-switch non sono valutabili.")
        if not s["power_law"].calibrated:
            w.append("Power law non calibrata dai documenti: uso parametri standard (Santostasi).")
        w.append(
            "Il capitale del piano deve essere denaro che puoi tenere fermo 4+ anni, separato dal "
            "fondo di emergenza. Questo software non è consulenza finanziaria."
        )


def _short(value: Any) -> str:
    text = str(value)
    return text if len(text) <= 90 else text[:87] + "…"
