"""Punto di ingresso: python src/main.py"""

import sys
from pathlib import Path

# Consente l'esecuzione diretta dello script senza installare il pacchetto
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt6.QtWidgets import QApplication  # noqa: E402

from btc_cycle import APP_NAME  # noqa: E402
from btc_cycle.gui.main_window import MainWindow  # noqa: E402
from btc_cycle.gui.style import QSS  # noqa: E402


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName("enkas79")
    app.setStyle("Fusion")
    app.setStyleSheet(QSS)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
