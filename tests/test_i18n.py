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
