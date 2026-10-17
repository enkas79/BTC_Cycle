"""Rendering del piano in HTML (GUI/export) e Markdown."""

from __future__ import annotations

import html
from typing import Any, List, Tuple

from ..i18n import fmt_date, tr, tr_label
from .planner import Plan, pct, usd

Block = Tuple[Any, ...]  # ("p", testo) | ("ul", [voci]) | ("table", intestazioni, righe) | ("warn", [voci])


_d = fmt_date


def build_sections(plan: Plan) -> List[Tuple[str, List[Block]]]:
    s, cur = plan.situation, plan.inputs.currency
    sections: List[Tuple[str, List[Block]]] = []

    sections.append((tr("Cosa fare adesso"), [("ul", plan.actions_now or [tr("Nessuna azione.")])]))

    rows = [
        [tr("Data analisi"), _d(s["today"])],
        [tr("Prezzo BTC"), usd(s["price"])],
        [tr("Ultimo halving"), tr("{d} ({days} giorni, {m:.1f} mesi)").format(
            d=_d(s["last_halving"]), days=s["days_since"], m=s["months_since"])],
        [tr("Fase del ciclo"), f"{s['phase'].name} — {s['phase'].description}"],
        [tr("Minimo stimato (H+offset)"), _d(s["est_bottom"])],
        [tr("Finestra di minimo"), f"{_d(s['window_start'])} – {_d(s['window_end'])}"],
    ]
    if s.get("ttl_window"):
        rows.append([tr("Minimo da massimo+12/13 mesi"),
                     f"{_d(s['ttl_window'][0])} – {_d(s['ttl_window'][1])}"])
    if s.get("ath"):
        rows.append([tr("Massimo di ciclo"), tr("{p} ({d}) — drawdown {dd}").format(
            p=usd(s["ath"]), d=_d(s.get("ath_date")), dd=pct(s["drawdown"]))])
    rows += [
        [tr("Fair value power law"), tr("{v} (prezzo {p})").format(v=usd(s["fair"]), p=pct(s["vs_fair"]))],
        [tr("Floor power law"), tr("{v} (prezzo {p})").format(v=usd(s["floor"]), p=pct(s["vs_floor"]))],
        [tr("Modello power law"), (
            tr("Fit sullo storico: esponente {b:.2f}, R² {r2:.3f}, floor = {q:.1f}° percentile dei residui")
            .format(b=s["pl_fit"].exponent, r2=s["pl_fit"].r2, q=s["pl_fit"].quantile * 100)
            if s["pl_source"] == "fit" else tr("Dai documenti (esponente {b:.2f})").format(
                b=s["power_law"].exponent))],
        [tr("Prossimo halving"), _d(s["next_halving"])],
    ]
    sections.append((tr("Situazione di mercato e ciclo"),
                     [("table", [tr("Voce"), tr("Valore")], rows)]))

    p = plan.pots
    blocks: List[Block] = [("table", [tr("Quota"), tr("Importo")], [
        [tr("Capitale totale"), f"{p['capital']:,.0f} {cur}"],
        [tr("Capitale 'finestra di minimo' ({p:.0f}%)").format(p=p["bottom_pct"]),
         f"{p['bottom']:,.0f} {cur}"],
        [tr("Capitale DCA esteso"), f"{p['dca']:,.0f} {cur}"],
        [tr("Non allocato"), f"{p['idle']:,.0f} {cur}"],
    ])]
    sections.append((tr("Ripartizione del capitale"), blocks))

    if p["bottom"]:
        factor = s.get("ladder_factor", 1.0)
        note = (tr("Zone riancorate al floor attuale (fattore {f:.3f}).").format(f=factor)
                if factor != 1.0 else tr("Zone come da documento."))
        ladder_rows = [
            [str(r["rung"]),
             (f"{usd(r['low'])} – {usd(r['high'])}" if r["low"] else f"< {usd(r['high'])}"),
             f"{r['pct']}%" + (tr(" + riserva flush") if r["plus_reserve"] else ""),
             f"{r['amount']:,.0f} {cur}", f"{r['btc']:.5f}", usd(r["trigger"]), r["status"]]
            for r in plan.ladder
        ]
        d, r = plan.drip, plan.reserve
        sections.append((tr("Finestra di minimo: ladder, drip e riserva"), [
            ("p", tr("Regola: un gradino scatta solo con una chiusura giornaliera sotto il minimo "
                     "di chiusura del ciclo (non con uno spike intraday). ") + note),
            ("table", ["#", tr("Zona"), tr("% capitale"), tr("Importo"), tr("BTC stimati"),
                       tr("Scatta a ≤"), tr("Stato")], ladder_rows),
            ("ul", [
                tr("Drip: {pct}% al giorno = {daily:,.0f} {cur} finché il prezzo è sotto il floor "
                   "({fl}); budget {tot:,.0f} {cur} ≈ {days} giorni. Stato: {st}.").format(
                    pct=d["pct"], daily=d["daily"], cur=cur, fl=usd(d["floor"]), tot=d["total"],
                    days=d["days"], st=tr("ATTIVO") if d["active"] else tr("in pausa")),
                tr("Riserva: {tot:,.0f} {cur}, di cui {fl:,.0f} per un flush violento (ultimo "
                   "gradino) e {bk:,.0f} di backstop.").format(
                    tot=r["total"], cur=cur, fl=r["flush"], bk=r["backstop"]),
                tr("Anti-miss: dal {d}, se sei sotto-investito, distribuisci il residuo in rate "
                   "settimanali (≥ {w:,.0f} {cur}/sett.) entro {e}.").format(
                    d=_d(r["anti_miss_date"]), w=r["weekly_min"], cur=cur, e=_d(r["window_end"])),
                tr("Mai comprare su candele verdi/rally; se il prezzo rompe al rialzo prima delle "
                   "zone profonde, passa a DCA semplice."),
            ]),
        ]))

    if p["dca"]:
        dca_rows = [[str(x["n"]), _d(x["date"]), f"{x['pct']:.2f}%", f"{x['amount']:,.0f} {cur}",
                     f"{x['max_amount']:,.0f} {cur}"] for x in plan.dca]
        b = plan.boost_now
        boost_rows = [[x["condition"], f"+{x['boost']}%",
                       tr("n/d") if x["active"] is None else (tr("SÌ") if x["active"] else tr("no"))]
                      for x in plan.boosters]
        kill = (tr("n/d (serve MA200)") if b["kill_switch"] is None
                else (tr("ATTIVO: boost sospesi") if b["kill_switch"] else tr("non attivo")))
        sections.append((tr("DCA esteso front-loaded"), [
            ("p", tr("Inizio: {d}. Rate mensili decrescenti (front-load).").format(d=_d(s["dca_start"]))),
            ("table", [tr("Mese"), tr("Data"), tr("% capitale DCA"), tr("Rata base"),
                       tr("Rata max con boost")], dca_rows),
            ("table", [tr("Boost"), tr("Incremento"), tr("Attivo ora")], boost_rows),
            ("ul", [tr("Boost totale attuale: +{t:.0f}% (tetto +{c:.0f}%).").format(t=b["total"], c=b["cap"]),
                    tr("Kill-switch (prezzo > MA200 +{p:.0f}%): {k}.").format(p=b["kill_pct"], k=kill)]
             + plan.dca_notes),
        ]))
    elif plan.dca_notes:
        sections.append((tr("DCA esteso"), [("ul", plan.dca_notes)]))

    sections.append((tr("Cosa comprare"), [("ul", plan.allocation)]))

    exit_rows = [[_d(x["date"]), f"H+{x['offset']} " + tr("mesi"), f"{x['sell_pct']}%",
                  f"{x['remaining']:.0f}%"] for x in plan.exit_steps]
    sections.append((tr("Piano di uscita (prossimo ciclo)"), [
        ("table", [tr("Data"), tr("Offset"), tr("Vendi (% posizione)"), tr("Residuo")], exit_rows),
        ("ul", plan.exit_notes),
    ]))

    if plan.levels:
        sections.append((tr("Livelli che decidono lo scenario"), [
            ("table", [tr("Livello"), tr("Prezzo"), tr("Tipo"), tr("Stato")],
             [[lv["name"], usd(lv["price"]), tr(lv["kind"]), lv["status"]] for lv in plan.levels]),
        ]))

    sc = plan.scenarios
    blocks = []
    if sc.get("bottom"):
        blocks.append(("table", [tr("Scenario minimo"), tr("Drawdown"), tr("Prezzo")],
                       [[b["name"], f"-{b['drawdown']}%", usd(b["price"])] for b in sc["bottom"]]))
    if sc.get("peak"):
        blocks.append(("table", [tr("Da minimo"), tr("Guadagno"), tr("Picco implicito")],
                       [[f"{x['bottom_name']} ({usd(x['bottom'])})", f"+{x['gain']}%",
                         usd(x["peak"])] for x in sc["peak"]]))
    if sc.get("target"):
        blocks.append(("p", tr("Obiettivo di picco dichiarato: {p}.")
                       .format(p=usd(sc["target"][0]["price"]))))
    if plan.bottom_estimates:
        blocks.append(("table", [tr("Fonte"), tr("Stima"), tr("Minimo"), tr("Massimo")],
                       [[e["doc_title"], tr_label(e["label"]), usd(e["low"]), usd(e["high"])]
                        for e in plan.bottom_estimates]))
    if blocks:
        sections.append((tr("Scenari e stime del minimo per fonte"), blocks))

    sections.append((tr("Avvertenze (partner critico)"), [("warn", plan.warnings)]))

    blocks = [("ul", plan.documents or [tr("Nessun documento: uso solo parametri predefiniti.")])]
    if plan.params_used:
        blocks.append(("table", [tr("Parametro"), tr("Valore"), tr("Fonte")],
                       [list(x) for x in plan.params_used]))
    sections.append((tr("Fonti e parametri usati"), blocks))
    return sections


CSS = """
body { font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; font-size: 10pt; color: #1f2430; }
h1 { font-size: 16pt; color: #b35900; margin-bottom: 2px; }
h2 { font-size: 12pt; color: #1f2430; border-bottom: 1px solid #f0a040; margin-top: 16px; }
table { border-collapse: collapse; margin: 6px 0; }
th { background: #2b3040; color: #ffffff; padding: 4px 8px; text-align: left; }
td { padding: 3px 8px; border-bottom: 1px solid #e3e6ec; }
.warn { color: #8a1c1c; }
.muted { color: #6b7280; font-size: 9pt; }
"""


def render_html(plan: Plan, title: str = "") -> str:
    title = title or tr("Piano di investimento Bitcoin")
    e = html.escape
    out = [f"<html><head><meta charset='utf-8'><title>{e(title)}</title>",
           f"<style>{CSS}</style></head><body>",
           f"<h1>{e(title)}</h1>",
           "<p class='muted'>" + e(tr("Generato il {d} · profilo {p} · non è consulenza finanziaria").format(
               d=_d(plan.situation["today"]), p=tr(plan.inputs.profile))) + "</p>"]
    for heading, blocks in build_sections(plan):
        out.append(f"<h2>{e(heading)}</h2>")
        for block in blocks:
            kind = block[0]
            if kind == "p":
                out.append(f"<p>{e(block[1])}</p>")
            elif kind in ("ul", "warn"):
                cls = " class='warn'" if kind == "warn" else ""
                out.append(f"<ul{cls}>" + "".join(f"<li>{e(i)}</li>" for i in block[1]) + "</ul>")
            elif kind == "table":
                head = "".join(f"<th>{e(h)}</th>" for h in block[1])
                body = "".join("<tr>" + "".join(f"<td>{e(str(c))}</td>" for c in row) + "</tr>"
                               for row in block[2])
                out.append(f"<table><tr>{head}</tr>{body}</table>")
    out.append("</body></html>")
    return "\n".join(out)


def render_markdown(plan: Plan, title: str = "") -> str:
    title = title or tr("Piano di investimento Bitcoin")
    out = [f"# {title}", "",
           "_" + tr("Generato il {d} · profilo {p} · non è consulenza finanziaria").format(
               d=_d(plan.situation["today"]), p=tr(plan.inputs.profile)) + "_", ""]
    for heading, blocks in build_sections(plan):
        out += [f"## {heading}", ""]
        for block in blocks:
            kind = block[0]
            if kind == "p":
                out += [block[1], ""]
            elif kind in ("ul", "warn"):
                prefix = "- ⚠️ " if kind == "warn" else "- "
                out += [prefix + i for i in block[1]] + [""]
            elif kind == "table":
                cells = lambda row: "| " + " | ".join(str(c).replace("|", "/") for c in row) + " |"  # noqa: E731
                out += [cells(block[1]), "|" + "---|" * len(block[1])]
                out += [cells(r) for r in block[2]] + [""]
    return "\n".join(out)
