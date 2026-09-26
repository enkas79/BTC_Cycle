"""Rendering del piano in HTML (GUI/export) e Markdown."""

from __future__ import annotations

import html
from typing import Any, List, Tuple

from .planner import Plan, pct, usd

Block = Tuple[Any, ...]  # ("p", testo) | ("ul", [voci]) | ("table", intestazioni, righe) | ("warn", [voci])


def _d(d) -> str:
    return d.strftime("%d/%m/%Y") if d else "n/d"


def build_sections(plan: Plan) -> List[Tuple[str, List[Block]]]:
    s, cur = plan.situation, plan.inputs.currency
    sections: List[Tuple[str, List[Block]]] = []

    sections.append(("Cosa fare adesso", [("ul", plan.actions_now or ["Nessuna azione."])]))

    rows = [
        ["Data analisi", _d(s["today"])],
        ["Prezzo BTC", usd(s["price"])],
        ["Ultimo halving", f"{_d(s['last_halving'])} ({s['days_since']} giorni, "
                           f"{s['months_since']:.1f} mesi)"],
        ["Fase del ciclo", f"{s['phase'].name} — {s['phase'].description}"],
        ["Minimo stimato (H+offset)", _d(s["est_bottom"])],
        ["Finestra di minimo", f"{_d(s['window_start'])} – {_d(s['window_end'])}"],
    ]
    if s.get("ttl_window"):
        rows.append(["Minimo da massimo+12/13 mesi",
                     f"{_d(s['ttl_window'][0])} – {_d(s['ttl_window'][1])}"])
    if s.get("ath"):
        rows.append(["Massimo di ciclo", f"{usd(s['ath'])} ({_d(s.get('ath_date'))}) — "
                                         f"drawdown {pct(s['drawdown'])}"])
    rows += [
        ["Fair value power law", f"{usd(s['fair'])} (prezzo {pct(s['vs_fair'])})"],
        ["Floor power law", f"{usd(s['floor'])} (prezzo {pct(s['vs_floor'])})"],
        ["Prossimo halving", _d(s["next_halving"])],
    ]
    sections.append(("Situazione di mercato e ciclo", [("table", ["Voce", "Valore"], rows)]))

    p = plan.pots
    blocks: List[Block] = [("table", ["Quota", "Importo"], [
        ["Capitale totale", f"{p['capital']:,.0f} {cur}"],
        [f"Capitale 'finestra di minimo' ({p['bottom_pct']:.0f}%)", f"{p['bottom']:,.0f} {cur}"],
        ["Capitale DCA esteso", f"{p['dca']:,.0f} {cur}"],
        ["Non allocato", f"{p['idle']:,.0f} {cur}"],
    ])]
    sections.append(("Ripartizione del capitale", blocks))

    if p["bottom"]:
        factor = s.get("ladder_factor", 1.0)
        note = (f"Zone riancorate al floor attuale (fattore {factor:.3f})." if factor != 1.0
                else "Zone come da documento.")
        ladder_rows = [
            [str(r["rung"]),
             (f"{usd(r['low'])} – {usd(r['high'])}" if r["low"] else f"< {usd(r['high'])}"),
             f"{r['pct']}%" + (" + riserva flush" if r["plus_reserve"] else ""),
             f"{r['amount']:,.0f} {cur}", f"{r['btc']:.5f}", usd(r["trigger"]), r["status"]]
            for r in plan.ladder
        ]
        d, r = plan.drip, plan.reserve
        sections.append(("Finestra di minimo: ladder, drip e riserva", [
            ("p", "Regola: un gradino scatta solo con una chiusura giornaliera sotto il minimo "
                  "di chiusura del ciclo (non con uno spike intraday). " + note),
            ("table", ["#", "Zona", "% capitale", "Importo", "BTC stimati", "Scatta a ≤",
                       "Stato"], ladder_rows),
            ("ul", [
                f"Drip: {d['pct']}% al giorno = {d['daily']:,.0f} {cur} finché il prezzo è sotto "
                f"il floor ({usd(d['floor'])}); budget {d['total']:,.0f} {cur} ≈ {d['days']} "
                f"giorni. Stato: {'ATTIVO' if d['active'] else 'in pausa'}.",
                f"Riserva: {r['total']:,.0f} {cur}, di cui {r['flush']:,.0f} per un flush "
                f"violento (ultimo gradino) e {r['backstop']:,.0f} di backstop.",
                f"Anti-miss: dal {_d(r['anti_miss_date'])}, se sei sotto-investito, distribuisci il "
                f"residuo in rate settimanali (≥ {r['weekly_min']:,.0f} {cur}/sett.) entro "
                f"{_d(r['window_end'])}.",
                "Mai comprare su candele verdi/rally; se il prezzo rompe al rialzo prima delle "
                "zone profonde, passa a DCA semplice.",
            ]),
        ]))

    if p["dca"]:
        dca_rows = [[str(x["n"]), _d(x["date"]), f"{x['pct']:.2f}%", f"{x['amount']:,.0f} {cur}",
                     f"{x['max_amount']:,.0f} {cur}"] for x in plan.dca]
        b = plan.boost_now
        boost_rows = [[x["condition"], f"+{x['boost']}%",
                       "n/d" if x["active"] is None else ("SÌ" if x["active"] else "no")]
                      for x in plan.boosters]
        kill = ("n/d (serve MA200)" if b["kill_switch"] is None
                else ("ATTIVO: boost sospesi" if b["kill_switch"] else "non attivo"))
        sections.append(("DCA esteso front-loaded", [
            ("p", f"Inizio: {_d(s['dca_start'])}. Rate mensili decrescenti (front-load)."),
            ("table", ["Mese", "Data", "% capitale DCA", "Rata base", "Rata max con boost"],
             dca_rows),
            ("table", ["Boost", "Incremento", "Attivo ora"], boost_rows),
            ("ul", [f"Boost totale attuale: +{b['total']:.0f}% (tetto +{b['cap']:.0f}%).",
                    f"Kill-switch (prezzo > MA200 +{b['kill_pct']:.0f}%): {kill}."]
             + plan.dca_notes),
        ]))
    elif plan.dca_notes:
        sections.append(("DCA esteso", [("ul", plan.dca_notes)]))

    sections.append(("Cosa comprare", [("ul", plan.allocation)]))

    exit_rows = [[_d(x["date"]), f"H+{x['offset']} mesi", f"{x['sell_pct']}%",
                  f"{x['remaining']:.0f}%"] for x in plan.exit_steps]
    sections.append(("Piano di uscita (prossimo ciclo)", [
        ("table", ["Data", "Offset", "Vendi (% posizione)", "Residuo"], exit_rows),
        ("ul", plan.exit_notes),
    ]))

    if plan.levels:
        sections.append(("Livelli che decidono lo scenario", [
            ("table", ["Livello", "Prezzo", "Tipo", "Stato"],
             [[lv["name"], usd(lv["price"]), lv["kind"], lv["status"]] for lv in plan.levels]),
        ]))

    sc = plan.scenarios
    blocks = []
    if sc.get("bottom"):
        blocks.append(("table", ["Scenario minimo", "Drawdown", "Prezzo"],
                       [[b["name"], f"-{b['drawdown']}%", usd(b["price"])] for b in sc["bottom"]]))
    if sc.get("peak"):
        blocks.append(("table", ["Da minimo", "Guadagno", "Picco implicito"],
                       [[f"{x['bottom_name']} ({usd(x['bottom'])})", f"+{x['gain']}%",
                         usd(x["peak"])] for x in sc["peak"]]))
    if sc.get("target"):
        blocks.append(("p", f"Obiettivo di picco dichiarato: {usd(sc['target'][0]['price'])}."))
    if plan.bottom_estimates:
        blocks.append(("table", ["Fonte", "Stima", "Minimo", "Massimo"],
                       [[e["doc_title"], e["label"], usd(e["low"]), usd(e["high"])]
                        for e in plan.bottom_estimates]))
    if blocks:
        sections.append(("Scenari e stime del minimo per fonte", blocks))

    sections.append(("Avvertenze (partner critico)", [("warn", plan.warnings)]))

    blocks = [("ul", plan.documents or ["Nessun documento: uso solo parametri predefiniti."])]
    if plan.params_used:
        blocks.append(("table", ["Parametro", "Valore", "Fonte"],
                       [list(x) for x in plan.params_used]))
    sections.append(("Fonti e parametri usati", blocks))
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


def render_html(plan: Plan, title: str = "Piano di investimento Bitcoin") -> str:
    e = html.escape
    out = [f"<html><head><meta charset='utf-8'><title>{e(title)}</title>",
           f"<style>{CSS}</style></head><body>",
           f"<h1>{e(title)}</h1>",
           f"<p class='muted'>Generato il {_d(plan.situation['today'])} · profilo "
           f"{e(plan.inputs.profile)} · non è consulenza finanziaria</p>"]
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


def render_markdown(plan: Plan, title: str = "Piano di investimento Bitcoin") -> str:
    out = [f"# {title}", "",
           f"_Generato il {_d(plan.situation['today'])} · profilo {plan.inputs.profile} · "
           "non è consulenza finanziaria_", ""]
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
