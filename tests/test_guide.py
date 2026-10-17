import os

import pytest

pytest.importorskip("PyQt6.QtGui")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.mark.parametrize("lang", ["it", "en"])
def test_guide_pdf(lang, tmp_path, monkeypatch):
    from PyQt6.QtGui import QGuiApplication

    from btc_cycle import guide

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841
    monkeypatch.setattr(guide, "data_dir", lambda: tmp_path)
    path = guide.build_guide_pdf(lang)
    data = open(path, "rb").read()
    assert data.startswith(b"%PDF") and len(data) > 20_000
    assert guide.build_guide_pdf(lang) == path  # seconda chiamata: riuso del file
