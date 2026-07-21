from pathlib import Path


def load_stylesheet(accent_color="#250a5c"):
    stylesheet_path = Path(__file__).resolve().parent.parent / "assets" / "themes" / "dark.css"
    close_icon_path = Path(__file__).resolve().parent.parent / "assets" / "icons" / "close.svg"
    close_icon_url = str(close_icon_path.resolve()) if close_icon_path.exists() else ""
    if stylesheet_path.exists():
        text = stylesheet_path.read_text(encoding="utf-8")
        return text.replace("{accent}", accent_color).replace("{close_icon}", close_icon_url)

    return f"""
    QWidget, QMainWindow, QToolBar, QDialog, QMenu, QTableWidget, QTableWidgetItem, QLineEdit, QPushButton, QLabel, QTextEdit, QScrollArea {{
        background: #121212;
        color: #e8eaed;
        border: 1px solid #2d2f33;
        selection-background-color: {accent_color};
        selection-color: #ffffff;
    }}
    QToolBar {{
        background: #18191d;
        spacing: 6px;
        padding: 4px;
    }}
    QLineEdit, QTextEdit {{
        background: #1f2126;
        border: 1px solid #2d2f33;
        border-radius: 0px;
        padding: 6px 8px;
        color: #e8eaed;
    }}
    QTabBar::tab {{
        background: #1e2025;
        color: #cfd5e0;
        padding: 8px 12px;
        border-top-left-radius: 0px;
        border-top-right-radius: 0px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {accent_color};
        color: #ffffff;
    }}
    QPushButton, QToolButton, QAction {{
        color: #e8eaed;
    }}
    QPushButton:hover, QToolButton:hover {{
        background: rgba(124, 77, 255, 0.15);
    }}
    QMenu {{
        background: #1f2126;
        color: #e8eaed;
        border: 1px solid #2d2f33;
    }}
    QHeaderView::section {{
        background: #24272d;
        color: #e8eaed;
        padding: 4px;
    }}
    """
