from btc_cycle import i18n
from btc_cycle.i18n import EN, tr


def test_tr_switch():
    i18n.set_lang("en")
    assert tr("Piano") == "Plan" and tr("testo ignoto") == "testo ignoto"
    i18n.set_lang("xx")  # lingua non supportata: ripiega sull'italiano
    assert tr("Piano") == "Piano"


def test_placeholders_match():
    import re
    for it, en in EN.items():
        assert sorted(re.findall(r"{\w+", it)) == sorted(re.findall(r"{\w+", en)), it


def test_every_tr_literal_has_translation():
    import ast
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent / "src"
    missing = []
    for path in root.rglob("*.py"):
        if path.name.startswith("i18n"):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tr"
                    and node.args and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str) and node.args[0].value not in EN):
                missing.append(f"{path.name}: {node.args[0].value}")
    assert not missing, missing


def test_english_plan_has_no_italian(kb):
    from datetime import date

    from btc_cycle.core.planner import PlanInputs, Planner
    from btc_cycle.core.report import render_markdown

    i18n.set_lang("en")
    try:
        md = render_markdown(Planner(kb).build(PlanInputs(
            capital=10000, btc_price_usd=64000, currency="USD", today=date(2026, 9, 26))))
    finally:
        i18n.set_lang("it")
    assert "What to do now" in md and "Cosa fare" not in md and "Avvertenze" not in md
    assert "2026-09-26" in md
