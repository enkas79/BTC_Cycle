from btc_cycle.core import extractors as ex

from .conftest import ACCUMULATION, POWER_LAW, PULLBACK, ROADMAP


def values(text, meta_date=None):
    _, ctx, insights = ex.analyze_pages([text], meta_date)
    return ctx, {i.key: i.value for i in insights if not i.key.startswith("level.")}


def test_money_parsing_ignores_following_words():
    assert ex.money_from("$58,000 today") == 58000
    assert ex.money_from("$50,000 Matches") == 50000
    assert ex.money_from("$35K–") == 35000
    assert ex.money_from("$1.1M") == 1_100_000
    assert ex.money_from("$4 billion") == 4e9


def test_roadmap():
    ctx, v = values(ROADMAP)
    assert ctx["doc_date"] == "2026-02-01"
    assert v["cycle.peak_offset_months"] == 18
    assert v["cycle.bottom_offset_months"] == 30
    assert v["cycle.accumulation_offsets"] == [30, 48]
    assert v["cycle.ath"] == {"price": 126272.0, "date": "2025-10-06"}
    assert v["cycle.drawdown_history"] == [93, 86, 84, 77]
    assert [s["price"] for s in v["cycle.bottom_scenarios"]] == [50000, 41600, 35300]
    assert v["cycle.bottom_range"]["timing"] == "Q4 2026"
    assert [b["pct"] for b in v["dca.front_load"]] == [40, 30, 20, 10]
    assert v["dca.booster_fear"] == {"threshold": 25, "boost": 25}
    assert v["dca.booster_cap"] == 50 and v["dca.kill_switch_pct"] == 40
    assert v["cycle.next_halving"] == "2028-04"
    assert v["cycle.days_to_peak_range"] == [500, 550]
    assert [s["offset_months"] for s in v["exit.schedule"]] == [12, 15, 18]
    assert v["exit.moonbag_pct"] == 25
    assert v["cycle.peak_target"] == 200000


def test_accumulation():
    ctx, v = values(ACCUMULATION)
    assert ctx["doc_date"] == "2026-07-22"
    assert v["accum.streams"] == {"ladder": 50, "drip": 30, "reserve": 20}
    zones = v["accum.ladder"]
    assert [z["pct"] for z in zones] == [10, 13, 16, 11]
    assert zones[-1]["plus_reserve"] and zones[-1]["high"] == 45000
    assert v["power_law.floor"]["low"] == 57000 and v["power_law.floor"]["high"] == 58000
    assert v["accum.drip_daily_pct"] == 1.0 and v["accum.drip_daily_pct_slow"] == 0.5
    assert v["accum.flush_pct"] == 10 and v["accum.anti_miss_weekly_pct"] == 3
    assert v["accum.window"] == {"start": "2026-08", "end": "2026-11"}
    assert v["rule.no_chase"] is True


def test_power_law_and_pullback():
    _, v = values(POWER_LAW)
    assert v["power_law.anchor"]["pct_below"] == 43
    assert v["power_law.floor_breaches"] == [33.0, 12.0]
    _, v = values(PULLBACK)
    assert v["levels.invalidation_up"]["price"] == 82833
    assert v["levels.invalidation_down"]["price"] == 57735
    assert v["cycle.top_to_low_months"] == [13.4, 12.0, 12.4]


def test_metadata():
    corpus = ex.Corpus([ROADMAP])
    assert ex.detect_source(corpus) == ("@bitcoin.daily", "bitcoindaily")
    assert any(f.startswith("promozionale") for f in ex.detect_flags(corpus, ""))
    assert ex.detect_title("a9ab6853-the-pullback-playbook.pdf", "x.html") == "The Pullback Playbook"
    assert ex.detect_title("f.pdf", "A Real Title") == "A Real Title"
