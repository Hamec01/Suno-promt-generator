THEMES = {
    "dark_noir": {
        "bg": "#0a0c10",
        "panel": "#12161c",
        "panel_soft": "#181d24",
        "text": "#f0f3f7",
        "muted": "#9ea8b7",
        "accent": "#8fb7ff",
        "accent_soft": "#22324d",
        "border": "#2a313b",
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
        padding: 8px 12px;
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
        min-width: 290px;
        min-height: 112px;
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

    QLabel[cardSecondary="true"] {{
        font-size: 11px;
        color: {p['muted']};
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
        padding: 10px 14px;
        margin-right: 6px;
        min-width: 120px;
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
