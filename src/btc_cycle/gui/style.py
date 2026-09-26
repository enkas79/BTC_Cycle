"""Tema QSS: neutro chiaro con accento arancio Bitcoin."""

ACCENT = "#f7931a"
ACCENT_DARK = "#b35900"
INK = "#1f2430"
NAVY = "#2b3040"

QSS = f"""
QMainWindow {{ background: #f5f6f8; }}
QWidget {{ font-size: 10pt; color: {INK}; }}
QTabWidget::pane {{ border: 1px solid #dfe2e8; border-radius: 6px; background: #ffffff; top: -1px; }}
QTabBar::tab {{
    padding: 8px 18px; margin-right: 2px; background: #e9ecf1; color: #4b5263;
    border-top-left-radius: 6px; border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{ background: #ffffff; color: {ACCENT_DARK}; font-weight: 600; }}
QPushButton {{
    padding: 6px 14px; border: 1px solid #cfd4dc; border-radius: 5px; background: #ffffff;
}}
QPushButton:hover {{ border-color: {ACCENT}; }}
QPushButton:disabled {{ color: #9aa1ad; }}
QPushButton#primary {{ background: {ACCENT}; color: #ffffff; border: none; font-weight: 600; }}
QPushButton#primary:hover {{ background: #e07f00; }}
QGroupBox {{
    border: 1px solid #dfe2e8; border-radius: 6px; margin-top: 16px;
    padding: 12px 8px 8px 8px; font-weight: 600;
}}
QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; color: {ACCENT_DARK}; }}
QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QDateEdit {{
    padding: 4px 6px; border: 1px solid #cfd4dc; border-radius: 4px; background: #ffffff;
    font-weight: normal;
}}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QDateEdit:focus {{
    border-color: {ACCENT};
}}
QCheckBox {{ font-weight: normal; }}
QLabel {{ font-weight: normal; }}
QLabel#hint {{ color: #6b7280; font-size: 9pt; }}
QHeaderView::section {{ background: {NAVY}; color: #ffffff; padding: 5px 8px; border: none; }}
QTableWidget {{
    gridline-color: #eceef2; alternate-background-color: #fafbfc;
    selection-background-color: #fde3c0; selection-color: {INK}; border: none;
}}
QTextBrowser {{ background: #ffffff; border: none; }}
QStatusBar {{ background: {NAVY}; color: #e5e7eb; }}
QStatusBar QLabel {{ color: #e5e7eb; }}
QMenuBar {{ background: #ffffff; border-bottom: 1px solid #dfe2e8; }}
QMenuBar::item:selected, QMenu::item:selected {{ background: #fde3c0; color: {INK}; }}
QProgressBar {{ border: 1px solid #cfd4dc; border-radius: 4px; text-align: center; }}
QProgressBar::chunk {{ background: {ACCENT}; }}
"""
