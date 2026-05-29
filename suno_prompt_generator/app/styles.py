THEMES = {
    "dark_noir": {
        "bg": "#071018",
        "panel": "#0d1a24",
        "panel_soft": "#101d29",
        "text": "#f1f5f9",
        "muted": "#8fa3b5",
        "accent": "#2f8cff",
        "accent_soft": "#153252",
        "border": "#23435c",
    },
    "blood_ritual": {
        "bg": "#0d090a",
        "panel": "#1a1012",
        "panel_soft": "#241518",
        "text": "#f2e9ea",
        "muted": "#b49fa1",
        "accent": "#cf4a56",
        "accent_soft": "#462027",
        "border": "#4e262d",
    },
    "cold_ambient": {
        "bg": "#090d12",
        "panel": "#101923",
        "panel_soft": "#14202d",
        "text": "#e9f2ff",
        "muted": "#93a8be",
        "accent": "#6bb6d9",
        "accent_soft": "#1f3f4f",
        "border": "#2a465a",
    },
    "fantasy_gold": {
        "bg": "#0c0b09",
        "panel": "#17140f",
        "panel_soft": "#211b13",
        "text": "#f7f1df",
        "muted": "#c0ae83",
        "accent": "#e4b95c",
        "accent_soft": "#4a3920",
        "border": "#5c4a28",
    },
}


def get_stylesheet(theme: str = "dark_noir") -> str:
    p = THEMES.get(theme, THEMES["dark_noir"])
    return f"""
    QWidget {{
        background-color: {p['bg']};
        color: {p['text']};
        font-size: 13px;
    }}

    QMainWindow {{
        background-color: {p['bg']};
    }}

    QLabel#mutedLabel {{
        color: {p['muted']};
    }}

    QFrame#panel {{
        background-color: {p['panel']};
        border: 1px solid {p['border']};
        border-radius: 14px;
    }}

    QPushButton {{
        background-color: {p['panel_soft']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        min-height: 36px;
        padding: 7px 12px;
        color: {p['text']};
        font-weight: 600;
    }}

    QPushButton:hover {{
        border: 1px solid {p['accent']};
    }}

    QPushButton[variant="accent"] {{
        background-color: {p['accent_soft']};
        border: 1px solid {p['accent']};
    }}

    QFrame[card="true"] {{
        min-width: 200px;
        min-height: 90px;
        background-color: {p['panel']};
        border: 1px solid {p['border']};
        border-radius: 14px;
    }}

    QFrame[card="true"][active="true"] {{
        background-color: {p['accent_soft']};
        border: 1px solid {p['accent']};
    }}

    QLabel[cardPrimary="true"] {{
        font-size: 15px;
        font-weight: 700;
        color: {p['text']};
    }}

    QLabel#TokenPrimary {{
        color: {p['text']};
        font-size: 14px;
        font-weight: 700;
    }}

    QLabel[cardSecondary="true"] {{
        font-size: 11px;
        color: {p['muted']};
    }}

    QLabel#TokenSecondary {{
        color: {p['muted']};
        font-size: 11px;
    }}

    QPushButton#CardIconButton {{
        min-width: 24px;
        max-width: 24px;
        min-height: 24px;
        max-height: 24px;
        padding: 0;
        border-radius: 8px;
    }}

    QComboBox, QLineEdit, QTextEdit {{
        background-color: {p['panel']};
        border: 1px solid {p['border']};
        border-radius: 10px;
        padding: 6px;
        color: {p['text']};
    }}

    QComboBox QAbstractItemView {{
        background-color: {p['panel']};
        border: 1px solid {p['border']};
        color: {p['text']};
        selection-background-color: {p['accent_soft']};
    }}

    QTabWidget::pane {{
        border: none;
    }}

    QTabBar::tab {{
        background: {p['panel_soft']};
        color: {p['muted']};
        border: 1px solid {p['border']};
        border-radius: 12px;
        padding: 8px 12px;
        margin-right: 8px;
        min-width: 140px;
        max-width: 160px;
        min-height: 58px;
        font-size: 13px;
        font-weight: 600;
    }}

    QTabBar::tab:selected {{
        color: #ffffff;
        border: 1px solid {p['accent']};
        background: {p['accent_soft']};
    }}

    QScrollArea {{
        border: none;
        background: transparent;
    }}

    QTableWidget {{
        background-color: {p['panel']};
        border: 1px solid {p['border']};
        border-radius: 12px;
        gridline-color: {p['border']};
    }}
    """
