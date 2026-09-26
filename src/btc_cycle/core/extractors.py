"""Estrazione di insight strutturati dal testo dei documenti.

Ogni estrattore è una funzione ``(Corpus, contesto) -> List[Insight]`` basata su
regole (regex). Aggiungere un pattern qui estende automaticamente l'analisi a
documenti futuri; i documenti già importati vengono rianalizzati quando cambia
``EXTRACTOR_VERSION``.
"""

from __future__ import annotations

import re
from bisect import bisect_right
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from .models import Insight

EXTRACTOR_VERSION = 1

MONTHS = {
    m: i
    for i, names in enumerate(
        [
            ("january", "jan"),
            ("february", "feb"),
            ("march", "mar"),
            ("april", "apr"),
            ("may",),
            ("june", "jun"),
            ("july", "jul"),
            ("august", "aug"),
            ("september", "sep", "sept"),
            ("october", "oct"),
            ("november", "nov"),
            ("december", "dec"),
        ],
        start=1,
    )
    for m in names
}
MONTH_RE = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?"
    r"|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)
# Importo in dollari: $126,272 · $35K · $1.1M · $4 billion
# Il suffisso a lettera singola vale solo se non seguito da altre lettere ("$58,000 today").
MONEY_RE = (
    r"\$\s?(\d[\d,]*(?:\.\d+)?)\s?([kKmMbB](?![a-zA-Z])|(?:thousand|million|billion|trillion)\b)?"
)
DASH = r"\s*(?:[–—-]|to)\s*"

WORD_NUMBERS = {
    "one": 1.0,
    "two": 2.0,
    "three": 3.0,
    "five": 5.0,
    "ten": 10.0,
    "half a": 0.5,
    "a few": 3.0,
    "a third": 33.0,
    "a quarter": 25.0,
    "half": 50.0,
}


# ---------------------------------------------------------------------------
# Utilità
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace(" ", " ")).strip()


def parse_money(number: str, suffix: Optional[str] = None) -> float:
    value = float(number.replace(",", ""))
    s = (suffix or "").lower()
    if s.startswith(("k", "th")):
        value *= 1_000
    elif s.startswith("m"):
        value *= 1_000_000
    elif s.startswith("b"):
        value *= 1_000_000_000
    elif s.startswith("t"):
        value *= 1_000_000_000_000
    return value


def money_from(text: str) -> Optional[float]:
    m = re.search(MONEY_RE, text)
    return parse_money(m.group(1), m.group(2)) if m else None


def parse_amount_word(text: str) -> Optional[float]:
    text = text.strip().lower()
    if text in WORD_NUMBERS:
        return WORD_NUMBERS[text]
    m = re.match(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def month_number(name: str) -> int:
    key = name.lower().rstrip(".")
    return MONTHS.get(key) or MONTHS[key[:3]]


def parse_date_text(text: str) -> Optional[str]:
    """Converte 'July 22, 2026' / 'Oct 6, 2025' / 'February 2026' in ISO."""
    text = text.strip().replace(".", "")
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    return None


class Corpus:
    """Testo normalizzato di tutte le pagine, con mappatura posizione -> pagina."""

    def __init__(self, pages: List[str]):
        parts, offsets, pos = [], [], 0
        for page in pages:
            norm = normalize(page)
            offsets.append(pos)
            parts.append(norm)
            pos += len(norm) + 1
        self.pages = parts
        self.offsets = offsets
        self.text = " ".join(parts)

    def page_of(self, pos: int) -> int:
        return max(1, bisect_right(self.offsets, pos))

    def finditer(self, pattern: str, flags: int = re.IGNORECASE):
        return re.finditer(pattern, self.text, flags)

    def search(self, pattern: str, flags: int = re.IGNORECASE):
        return re.search(pattern, self.text, flags)

    def snippet(self, m: re.Match, pad: int = 30) -> str:
        start, end = max(0, m.start() - pad), min(len(self.text), m.end() + pad)
        return ("…" if start else "") + self.text[start:end] + ("…" if end < len(self.text) else "")

    def contains(self, pattern: str) -> bool:
        return self.search(pattern) is not None


def _ins(corpus: Corpus, m: re.Match, category: str, key: str, value: Any, label: str) -> Insight:
    return Insight(category, key, value, label, corpus.snippet(m), corpus.page_of(m.start()))


# ---------------------------------------------------------------------------
# Metadati: titolo, data, fonte, flag
# ---------------------------------------------------------------------------


def detect_title(filename: str, meta_title: str) -> str:
    bad = (not meta_title) or meta_title.lower().endswith((".html", ".htm")) or meta_title in (
        "(anonymous)",
        "untitled",
    )
    if not bad and len(meta_title) > 3:
        return meta_title
    stem = Path(filename).stem
    stem = re.sub(r"^[0-9a-f]{8}-", "", stem)  # prefisso hash degli upload
    words = re.split(r"[-_\s]+", stem)
    return " ".join(w if w.isdigit() else w.capitalize() for w in words if w)


def detect_date(corpus: Corpus, meta_date: Optional[str]) -> Optional[str]:
    m = corpus.search(rf"Compiled ({MONTH_RE} \d{{1,2}}, \d{{4}})")
    if m:
        return parse_date_text(m.group(1))
    first = corpus.pages[0] if corpus.pages else ""
    m = re.search(rf"\b({MONTH_RE} (?:\d{{1,2}}, )?20\d\d)\b", first)
    if m:
        parsed = parse_date_text(m.group(1))
        if parsed:
            return parsed
    return meta_date


def detect_source(corpus: Corpus) -> Tuple[str, str]:
    """Restituisce (nome visualizzato, chiave normalizzata) della fonte principale."""
    handles = Counter(
        h.rstrip(".").lower()
        for h in re.findall(r"(?<![\w.])@([A-Za-z0-9_.]{3,30})", corpus.text)
    )
    domains = Counter(
        d.lower()
        for d in re.findall(r"\b([a-z0-9-]+\.(?:com|vip|io|net|org|co))\b", corpus.text, re.I)
    )
    if handles:
        name = "@" + handles.most_common(1)[0][0]
    elif domains:
        name = domains.most_common(1)[0][0]
    else:
        return "sconosciuta", ""
    key = re.sub(r"\.(com|vip|io|net|org|co)$", "", name.lstrip("@"))
    return name, re.sub(r"[^a-z0-9]", "", key)


def detect_flags(corpus: Corpus, meta_title: str) -> List[str]:
    flags = []
    promo = len(
        re.findall(
            r"discord|checkout|join the|for members|\.vip\b|lead ?magnet|subscribe|live read",
            corpus.text + " " + meta_title,
            re.I,
        )
    )
    if promo >= 2 or "leadmagnet" in meta_title.lower():
        flags.append("promozionale (funnel verso contenuti a pagamento)")
    if corpus.contains(r"not financial advice"):
        flags.append("disclaimer: non è consulenza finanziaria")
    if corpus.contains(r"small samples?|small distributions"):
        flags.append("campioni statistici ridotti dichiarati")
    return flags


# ---------------------------------------------------------------------------
# Estrattori tematici
# ---------------------------------------------------------------------------

Ctx = Dict[str, Any]


def extract_cycle(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    offsets = [
        ("Estimated Peak", "cycle.peak_offset_months", "Picco stimato (mesi dopo halving)"),
        ("Estimated Bottom", "cycle.bottom_offset_months", "Minimo stimato (mesi dopo halving)"),
        ("DCA Start Window", "cycle.dca_start_offset_months", "Inizio DCA (mesi dopo halving)"),
    ]
    for name, key, label in offsets:
        m = c.search(rf"{name}\s*H\s*\+\s*(\d{{1,2}})\s*m")
        if m:
            out.append(_ins(c, m, "ciclo", key, int(m.group(1)), label))
    m = c.search(r"Accumulation\s*H\s*\+\s*(\d{1,2})\s*m\w*\s*(?:→|->|to|[–-])\s*H\s*\+\s*(\d{1,2})")
    if m:
        out.append(
            _ins(c, m, "ciclo", "cycle.accumulation_offsets", [int(m.group(1)), int(m.group(2))],
                 "Accumulo primario (mesi dopo halving)")
        )
    m = c.search(r"(?:peak|top)[^.]{0,40}?(\d{3})\s*[–-]\s*(\d{3})\s*days|(\d{3})\s*[–-]\s*(\d{3})"
                 r"\s*days[^.]{0,40}?(?:peak|top)")
    if m:
        a, b = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), m.group(4))
        out.append(_ins(c, m, "ciclo", "cycle.days_to_peak_range", [int(a), int(b)],
                        "Giorni halving → picco"))
    m = c.search(rf"Cycle High\s*{MONEY_RE}\s*\(({MONTH_RE}\.? \d{{1,2}}, \d{{4}})\)")
    if m:
        out.append(
            _ins(c, m, "ciclo", "cycle.ath",
                 {"price": parse_money(m.group(1), m.group(2)), "date": parse_date_text(m.group(3))},
                 "Massimo di ciclo")
        )
    m = c.search(r"(-\d{1,2}%(?:\s*(?:→|->)\s*-\d{1,2}%){2,})")
    if m:
        vals = [int(v) for v in re.findall(r"-(\d{1,2})%", m.group(1))]
        out.append(_ins(c, m, "ciclo", "cycle.drawdown_history", vals, "Drawdown storici dei bear (%)"))
    m = c.search(r"(?<![-\d,])(\d[\d,]*%(?:\s*(?:→|->)\s*\d[\d,]*%){2,})")
    if m:
        vals = [int(v.replace(",", "")) for v in re.findall(r"(\d[\d,]*)%", m.group(1))]
        out.append(_ins(c, m, "ciclo", "cycle.return_history", vals,
                        "Rendimenti minimo→picco per ciclo (%)"))
    matches = list(c.finditer(
        rf"(Conservative|Base Case|Aggressive|Bear Case|Bull Case|Worst Case)\s*-(\d{{1,2}})%\s*~?"
        rf"{MONEY_RE}"
    ))
    if matches:
        scenarios = [
            {"name": m.group(1), "drawdown": int(m.group(2)),
             "price": parse_money(m.group(3), m.group(4))}
            for m in matches
        ]
        out.append(_ins(c, matches[0], "ciclo", "cycle.bottom_scenarios", scenarios,
                        "Scenari di minimo (drawdown dal massimo)"))
    m = c.search(rf"bottom\D{{0,40}}?{MONEY_RE}{DASH}{MONEY_RE}(?:\s*\|?\s*(Q[1-4] \d{{4}}))?")
    if m:
        out.append(
            _ins(c, m, "ciclo", "cycle.bottom_range",
                 {"low": parse_money(m.group(1), m.group(2)),
                  "high": parse_money(m.group(3), m.group(4)), "timing": m.group(5)},
                 "Range del minimo di ciclo")
        )
    m = c.search(r"\+(\d{2,3})\s*[–-]\s*(\d{2,3})%")
    if m:
        out.append(_ins(c, m, "ciclo", "cycle.next_gain_range", [int(m.group(1)), int(m.group(2))],
                        "Guadagno atteso minimo→picco successivo (%)"))
    m = c.search(rf"Target:\s*~?{MONEY_RE}")
    if m:
        out.append(_ins(c, m, "ciclo", "cycle.peak_target", parse_money(m.group(1), m.group(2)),
                        "Obiettivo di picco"))
    m = c.search(r"((?:\d{1,2}\.\d,?\s*(?:and\s*)?){2,})months after their cycle tops")
    if m:
        vals = [float(v) for v in re.findall(r"\d{1,2}\.\d", m.group(1))]
        out.append(_ins(c, m, "ciclo", "cycle.top_to_low_months", vals,
                        "Mesi dal massimo al minimo (cicli passati)"))
    m = c.search(rf"next halving:?\s*({MONTH_RE})\s+(\d{{4}})")
    if m:
        iso = parse_date_text(f"{m.group(1)} {m.group(2)}")
        out.append(_ins(c, m, "ciclo", "cycle.next_halving", iso[:7] if iso else None,
                        "Prossimo halving"))
    m = c.search(r"When (\d)\+ align")
    if m:
        out.append(_ins(c, m, "bottom", "bottom.confluence_min", int(m.group(1)),
                        "Segnali di bottom minimi in confluenza"))
    m = c.search(r"Fear\s*&\s*Greed Sustained Below (\d{1,2})")
    if m:
        out.append(_ins(c, m, "bottom", "bottom.fear_greed_sustained", int(m.group(1)),
                        "Fear & Greed sostenuto sotto"))
    m = c.search(r"Weekly RSI Below (\d{2})")
    if m:
        out.append(_ins(c, m, "bottom", "bottom.weekly_rsi_below", int(m.group(1)),
                        "RSI settimanale sotto (bottom)"))
    return out


def extract_power_law(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    m = c.search(
        rf"{MONEY_RE}[^$]{{0,60}}?(\d{{1,2}})\s*(?:%|percent) below (?:the model's |the )?"
        r"(?:fair value|center line)"
    )
    if m:
        out.append(
            _ins(c, m, "power_law", "power_law.anchor",
                 {"price": parse_money(m.group(1), m.group(2)), "pct_below": int(m.group(3)),
                  "date": ctx.get("doc_date")},
                 "Prezzo vs fair value power law")
        )
    m = c.search(rf"floor[^$]{{0,60}}?{MONEY_RE}{DASH}{MONEY_RE}")
    if m:
        out.append(
            _ins(c, m, "power_law", "power_law.floor",
                 {"low": parse_money(m.group(1), m.group(2)),
                  "high": parse_money(m.group(3), m.group(4)), "date": ctx.get("doc_date")},
                 "Floor (banda inferiore) power law")
        )
    m = c.search(r"closed below")
    if m:
        window = c.text[m.start(): m.start() + 300]
        vals = []
        for w in re.findall(
            r"(a third|a quarter|half|\d{1,2}(?:\.\d)?\s*(?:%|percent))\s+(?:under|below)", window,
            re.I,
        ):
            v = parse_amount_word(w)
            if v:
                vals.append(v)
        if vals:
            out.append(_ins(c, m, "power_law", "power_law.floor_breaches", vals,
                            "Rotture storiche del floor (% sotto)"))
    m = c.search(r"(?:power[- ]law )?(?:exponent|slope)\s*(?:of|=|:)?\s*(\d\.\d+)")
    if m and c.contains(r"power[- ]law"):
        out.append(_ins(c, m, "power_law", "power_law.exponent", float(m.group(1)),
                        "Esponente power law"))
    return out


def extract_accumulation(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    streams: Dict[str, int] = {}
    names = {"level ladder": "ladder", "daily drip": "drip", "dry powder": "reserve"}
    first = None
    for m in c.finditer(r"(\d{1,3})\s*%\s*(?:the\s+)?(level ladder|daily drip|dry powder)"):
        streams[names[m.group(2).lower()]] = int(m.group(1))
        first = first or m
    if len(streams) >= 2 and first:
        out.append(_ins(c, first, "accumulo", "accum.streams", streams,
                        "Ripartizione flussi (ladder/drip/riserva %)"))
    if c.contains(r"ladder"):
        zones = []
        first = None
        for m in c.finditer(rf"{MONEY_RE}{DASH}{MONEY_RE}\s+(\d{{1,2}})\s*%"):
            lo, hi = parse_money(m.group(1), m.group(2)), parse_money(m.group(3), m.group(4))
            if lo >= 1000:
                zones.append({"low": min(lo, hi), "high": max(lo, hi), "pct": int(m.group(5)),
                              "plus_reserve": False})
                first = first or m
        for m in c.finditer(
            rf"Below (?:about )?{MONEY_RE}[^%$]{{0,40}}?(\d{{1,2}})\s*%\s*(\+\s*reserve)?"
        ):
            zones.append({"low": 0.0, "high": parse_money(m.group(1), m.group(2)),
                          "pct": int(m.group(3)), "plus_reserve": bool(m.group(4))})
            first = first or m
        if zones and first:
            zones.sort(key=lambda z: -z["high"])
            out.append(_ins(c, first, "accumulo", "accum.ladder", zones,
                            "Zone della ladder (% del capitale)"))
    m = c.search(r"buy about (\d+(?:\.\d+)?|one|half a) (?:%|percent) of your pot")
    if not m:
        m = c.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent) (?:of your pot )?(?:a|per|every) day")
    if m:
        out.append(_ins(c, m, "accumulo", "accum.drip_daily_pct", parse_amount_word(m.group(1)),
                        "Drip giornaliero (% del capitale)"))
    m = c.search(r"(?:halve it to )(half a|\d+(?:\.\d+)?) (?:%|percent) a day")
    if m:
        out.append(_ins(c, m, "accumulo", "accum.drip_daily_pct_slow",
                        parse_amount_word(m.group(1)), "Drip giornaliero lento (%)"))
    m = c.search(r"(?:around|about) (\w+|\d+) (?:%|percent)[^.]{0,40}flush")
    if m:
        val = parse_amount_word(m.group(1))
        if val:
            out.append(_ins(c, m, "accumulo", "accum.flush_pct", val,
                            "Riserva per flush violento (%)"))
    m = c.search(r"(a few|\d+) (?:%|percent) a week")
    if m:
        out.append(_ins(c, m, "accumulo", "accum.anti_miss_weekly_pct",
                        parse_amount_word(m.group(1)), "Anti-miss: % a settimana"))
    for m in c.finditer(rf"\b({MONTH_RE})\.? to ({MONTH_RE})\b"):
        around = c.text[max(0, m.start() - 80): m.end() + 80].lower()
        if "window" in around:
            year = int((ctx.get("doc_date") or str(date.today().year))[:4])
            s, e = month_number(m.group(1)), month_number(m.group(2))
            out.append(_ins(c, m, "accumulo", "accum.window",
                            {"start": f"{year}-{s:02d}",
                             "end": f"{year + (1 if e < s else 0)}-{e:02d}"},
                            "Finestra di accumulo"))
            break
    rules = [
        (r"daily close, not a wick", "rule.new_low_daily_close",
         "Nuovo minimo = chiusura giornaliera, non spike"),
        (r"never chase green", "rule.no_chase", "Mai comprare nei rally (no FOMO)"),
        (r"shift to plain DCA", "rule.breakout_plain_dca",
         "Se rompe al rialzo prima: passa a DCA semplice"),
        (r"no leverage", "rule.no_leverage", "Nessuna leva"),
    ]
    for pattern, key, label in rules:
        m = c.search(pattern)
        if m:
            out.append(_ins(c, m, "regole", key, True, label))
    return out


def extract_dca(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    blocks, first = [], None
    for m in c.finditer(r"Months?\s*(\d{1,2})\s*[–-]\s*(\d{1,2})\s*(\d{1,3})\s*%"):
        blocks.append({"from": int(m.group(1)), "to": int(m.group(2)), "pct": int(m.group(3))})
        first = first or m
    if len(blocks) >= 2 and first:
        out.append(_ins(c, first, "dca", "dca.front_load", blocks,
                        "DCA front-loaded (% per blocco di mesi)"))
    patterns = [
        (r"-?(\d{1,2})% from (?:the )?rolling 200-day high\s*\+(\d{1,2})%", "dca.booster_drawdown",
         "Boost se -X% dal massimo 200gg"),
        (r"Fear\s*(?:&|and)\s*Greed(?: Index)? below (\d{1,2})\s*\+(\d{1,2})%", "dca.booster_fear",
         "Boost se Fear & Greed sotto X"),
        (r"VIX\s*>\s*(\d{1,2})[^+]{0,40}\+(\d{1,2})%", "dca.booster_vix", "Boost se VIX sopra X"),
    ]
    for pattern, key, label in patterns:
        m = c.search(pattern)
        if m:
            out.append(_ins(c, m, "dca", key,
                            {"threshold": int(m.group(1)), "boost": int(m.group(2))}, label))
    m = c.search(r"MAXIMUM per month\s*\+(\d{1,3})%")
    if m:
        out.append(_ins(c, m, "dca", "dca.booster_cap", int(m.group(1)), "Boost massimo mensile (%)"))
    m = c.search(r"closes\s*>\s*\+?(\d{1,3})% above (?:the )?200-day MA")
    if m:
        out.append(_ins(c, m, "dca", "dca.kill_switch_pct", int(m.group(1)),
                        "Kill-switch boost: % sopra MA200"))
    m = c.search(r"total amount for (\d{1,2})\s*[–-]\s*(\d{1,2}) months")
    if m:
        out.append(_ins(c, m, "dca", "dca.duration_months", [int(m.group(1)), int(m.group(2))],
                        "Durata DCA (mesi)"))
    m = c.search(r"First (\d{1,2}) months = (\d{1,3})% BTC \(up to (\d{1,2})% ETH\)")
    if m:
        out.append(_ins(c, m, "allocazione", "alloc.initial",
                        {"months": int(m.group(1)), "btc_pct": int(m.group(2)),
                         "eth_max_pct": int(m.group(3))},
                        "Allocazione iniziale"))
    m = c.search(
        r"Next (\d{1,2})\s*[–-]\s*(\d{1,2}) months = diversify (\d{1,2})\s*[–-]\s*(\d{1,2})% "
        r"into top-(\d+) alts"
    )
    if m:
        out.append(_ins(c, m, "allocazione", "alloc.alts",
                        {"from_month": int(m.group(1)), "to_month": int(m.group(2)),
                         "min_pct": int(m.group(3)), "max_pct": int(m.group(4)),
                         "top": int(m.group(5))},
                        "Diversificazione in altcoin"))
    return out


def extract_exit(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    steps, first = [], None
    for m in c.finditer(rf"H\s*\+\s*(\d{{1,2}})\s*months?\s*\({MONTH_RE}\s*\d{{4}}\)\s*Sell\s*(\d{{1,2}})%"):
        steps.append({"offset_months": int(m.group(1)), "sell_pct": int(m.group(2))})
        first = first or m
    if steps and first:
        out.append(_ins(c, first, "uscita", "exit.schedule", steps,
                        "Vendite programmate (mesi dopo halving)"))
    m = c.search(r"Keep\s*(\d{1,2})%\s*(?:Hold forever|moon)")
    if m:
        out.append(_ins(c, m, "uscita", "exit.moonbag_pct", int(m.group(1)),
                        "Quota da tenere per sempre (%)"))
    m = c.search(r"Weekly RSI above (\d{2})")
    if m:
        out.append(_ins(c, m, "uscita", "exit.weekly_rsi_above", int(m.group(1)),
                        "RSI settimanale sopra (top)"))
    m = c.search(r"When (\d)\+ appear")
    if m:
        out.append(_ins(c, m, "uscita", "exit.euphoria_min", int(m.group(1)),
                        "Segnali di euforia minimi"))
    return out


def extract_levels(c: Corpus, ctx: Ctx) -> List[Insight]:
    out: List[Insight] = []
    for m in c.finditer(
        rf"((?:{MONTH_RE}) (?:high|low))\s*{MONEY_RE}\s*A (?:daily )?close (above|below)"
    ):
        key = "levels.invalidation_up" if m.group(4).lower() == "above" else "levels.invalidation_down"
        label = ("Livello rialzista (chiusura sopra = trend cambia)" if key.endswith("up")
                 else "Livello ribassista (chiusura sotto = gamba finale)")
        out.append(_ins(c, m, "livelli", key,
                        {"name": m.group(1), "price": parse_money(m.group(2), m.group(3))}, label))
    stats = [
        (r"\+(\d{1,3})%\s*median peak of a failed bear rally", "stats.failed_rally_median_gain",
         "Rally ribassista fallito: guadagno mediano (%)"),
        (r"-(\d{1,2})%\s*median fall", "stats.failed_rally_median_fall",
         "Dopo rally fallito: calo mediano (%)"),
        (r"-(\d{1,2})%\s*median pullback", "stats.true_bottom_median_pullback",
         "Pullback mediano anche a bottom confermato (%)"),
    ]
    for pattern, key, label in stats:
        m = c.search(pattern)
        if m:
            out.append(_ins(c, m, "statistiche", key, int(m.group(1)), label))
    m = c.search(r"rallied (\d{1,3})% off its (\w+) low")
    if m:
        out.append(_ins(c, m, "mercato", "market.rally_from_low",
                        {"pct": int(m.group(1)), "ref": m.group(2)}, "Rally dal minimo recente"))
    for m in c.finditer(rf"({MONTH_RE})'s median return is (-?\d+(?:\.\d+)?)%"):
        out.append(_ins(c, m, "stagionalità", f"season.{m.group(1).lower()[:3]}",
                        float(m.group(2)), f"Rendimento mediano di {m.group(1)} (%)"))
    return out


LEVEL_TAGS = [
    ("fair_value", r"fair value|center line"),
    ("supporto", r"bottom|floor|support|low\b|lows\b|capitulat"),
    ("obiettivo", r"peak|top\b|target|resistance|high\b"),
]


def extract_generic_levels(c: Corpus, ctx: Ctx) -> List[Insight]:
    """Livelli di prezzo BTC (1k–10M $) classificati dal contesto: utile per documenti nuovi."""
    out: List[Insight] = []
    seen = set()
    for m in c.finditer(MONEY_RE):
        price = parse_money(m.group(1), m.group(2))
        if not 1_000 <= price <= 10_000_000:
            continue
        before = c.text[max(0, m.start() - 60): m.start()].lower()
        tag = next((t for t, pat in LEVEL_TAGS if re.search(pat, before)), None)
        if not tag or (tag, price) in seen:
            continue
        seen.add((tag, price))
        out.append(_ins(c, m, "livelli", f"level.{tag}", price, f"Livello citato ({tag})"))
    return out


EXTRACTORS: List[Callable[[Corpus, Ctx], List[Insight]]] = [
    extract_cycle,
    extract_power_law,
    extract_accumulation,
    extract_dca,
    extract_exit,
    extract_levels,
    extract_generic_levels,
]


def analyze_pages(pages: List[str], meta_date: Optional[str] = None) -> Tuple[Corpus, Ctx, List[Insight]]:
    corpus = Corpus(pages)
    ctx: Ctx = {"doc_date": detect_date(corpus, meta_date)}
    insights: List[Insight] = []
    for extractor in EXTRACTORS:
        try:
            insights.extend(extractor(corpus, ctx))
        except Exception as exc:  # un estrattore difettoso non blocca gli altri
            insights.append(Insight("errore", f"error.{extractor.__name__}", str(exc),
                                    "Errore di estrazione"))
    return corpus, ctx, insights
