from __future__ import annotations

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QCheckBox,
    QScrollArea,
    QSplitter,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)

from .flow_layout import FlowLayout
from .i18n import t
from .import_export import (
    build_combined_export,
    default_export_filename,
    detect_import_payload,
    load_json_file,
    merge_presets_with_stats,
    merge_prompt_data_with_stats,
    merge_user_prompts_with_stats,
    merge_smart_rules_with_stats,
    save_json_file,
)
from .prompt_builder import build_short_prompt
from .smart_generator import smart_generate_prompt
from .storage import Storage
from .styles import get_stylesheet


TAB_ICONS = {
    "genres": "🎼",
    "quality": "🎚️",
    "instruments": "🎻",
    "vocals": "🗣",
    "mood": "🌙",
    "texture": "🌫",
    "fantasy": "🛡",
    "horror": "💀",
    "hiphop": "🎛",
    "ambient": "🌌",
    "game_bgm": "🎮",
    "favorites": "⭐",
    "saved": "💾",
}

CARD_SIZES = {
    "small": {"width": 160, "height": 70},
    "medium": {"width": 220, "height": 95},
    "large": {"width": 280, "height": 120},
}

QUALITY_GROUP_LABELS = {
    "quality_general": {"en": "General Quality", "ru": "Общее качество"},
    "quality_fidelity": {"en": "Fidelity", "ru": "Точность / Fidelity"},
    "quality_mastering": {"en": "Mastering", "ru": "Мастеринг"},
    "quality_mixing": {"en": "Mixing", "ru": "Сведение"},
    "quality_stereo_space": {"en": "Stereo / Space", "ru": "Стерео / Пространство"},
    "quality_eq_tone": {"en": "EQ / Tone", "ru": "EQ / Тон"},
    "quality_dynamics_loudness": {"en": "Dynamics / Loudness", "ru": "Динамика / Громкость"},
    "quality_reverb_delay": {"en": "Reverb / Delay", "ru": "Реверб / Delay"},
    "quality_vocal_mix": {"en": "Vocal Mix", "ru": "Вокальный микс"},
    "quality_drums_mix": {"en": "Drums Mix", "ru": "Барабанный микс"},
    "quality_bass_low_end": {"en": "Bass / Low End", "ru": "Бас / Низ"},
    "quality_analog_tape": {"en": "Analog / Tape", "ru": "Аналог / Пленка"},
    "quality_lofi_grit": {"en": "Lo-Fi / Grit", "ru": "Lo-Fi / Грит"},
    "quality_clean_modern": {"en": "Clean / Modern", "ru": "Чистый / Современный"},
    "quality_live_acoustic": {"en": "Live / Acoustic", "ru": "Живой / Акустика"},
    "quality_cinematic_space": {"en": "Cinematic Space", "ru": "Кино-пространство"},
    "quality_negative_artifacts": {"en": "Negative Artifacts", "ru": "Нежелательные артефакты"},
    "quality_structured_meta_tags": {"en": "Structured Meta Tags", "ru": "Structured meta-теги"},
}

INSTRUMENT_GROUP_ICONS = {
    "instrument_keys_piano": "🎹",
    "instrument_keys_electric": "🎛️",
    "instrument_keys_organs": "⛪",
    "instrument_strings_bowed": "🎻",
    "instrument_strings_plucked": "🪕",
    "instrument_strings_ethnic": "🪕",
    "instrument_woodwinds": "🪈",
    "instrument_brass": "🎺",
    "instrument_percussion_drums": "🥁",
    "instrument_percussion_ethnic": "🪘",
    "instrument_percussion_mallets_bells": "🔔",
    "instrument_synths_general": "🎚️",
    "instrument_synths_analog": "📼",
    "instrument_synths_bass": "🔊",
    "instrument_hiphop_dj": "🎧",
    "instrument_choirs_vocal_textures": "👥",
    "instrument_horror_experimental": "💀",
    "instrument_ambient_textures": "🌫️",
    "instrument_orchestral_sections": "🎼",
    "instrument_sound_design_fx": "⚡",
}

INSTRUMENT_GROUP_LABELS = {
    "instrument_keys_piano": {"en": "Keys / Piano", "ru": "Клавишные / пианино"},
    "instrument_keys_electric": {"en": "Electric Keys", "ru": "Электро-клавиши"},
    "instrument_keys_organs": {"en": "Organs", "ru": "Органы"},
    "instrument_strings_bowed": {"en": "Bowed Strings", "ru": "Смычковые струнные"},
    "instrument_strings_plucked": {"en": "Plucked Strings", "ru": "Щипковые струнные"},
    "instrument_strings_ethnic": {"en": "Ethnic Strings", "ru": "Этнические струнные"},
    "instrument_woodwinds": {"en": "Woodwinds", "ru": "Деревянные духовые"},
    "instrument_brass": {"en": "Brass", "ru": "Медные духовые"},
    "instrument_percussion_drums": {"en": "Drums", "ru": "Барабаны"},
    "instrument_percussion_ethnic": {"en": "Ethnic Percussion", "ru": "Этническая перкуссия"},
    "instrument_percussion_mallets_bells": {"en": "Bells / Mallets", "ru": "Колокольчики / молоточковые"},
    "instrument_synths_general": {"en": "Synths", "ru": "Синты"},
    "instrument_synths_analog": {"en": "Analog Synths", "ru": "Аналоговые синты"},
    "instrument_synths_bass": {"en": "Synth Bass", "ru": "Синт-бас"},
    "instrument_hiphop_dj": {"en": "Hip-Hop / DJ", "ru": "Хип-хоп / DJ"},
    "instrument_choirs_vocal_textures": {"en": "Choirs", "ru": "Хоры"},
    "instrument_horror_experimental": {"en": "Horror / Experimental", "ru": "Хоррор / экспериментальные"},
    "instrument_ambient_textures": {"en": "Ambient Textures", "ru": "Эмбиент-текстуры"},
    "instrument_orchestral_sections": {"en": "Orchestral Sections", "ru": "Оркестровые секции"},
    "instrument_sound_design_fx": {"en": "Sound Design FX", "ru": "Sound Design FX"},
}

GENRE_GROUP_ICONS = {
    "genre_rap_general": "🎤",
    "genre_boom_bap": "🥁",
    "genre_trap_drill": "🔫",
    "genre_phonk_memphis": "🚗",
    "genre_cloud_emo_rap": "☁️",
    "genre_rnb_soul": "💞",
    "genre_pop": "✨",
    "genre_electronic_general": "🎛️",
    "genre_house": "🏠",
    "genre_techno": "⚙️",
    "genre_trance": "🌀",
    "genre_dnb_jungle": "⚡",
    "genre_breakbeat_garage": "🧩",
    "genre_dub_reggae": "🌴",
    "genre_ambient": "🌌",
    "genre_drone": "🛰️",
    "genre_lofi_tape": "📼",
    "genre_cinematic_score": "🎬",
    "genre_game_music": "🎮",
    "genre_fantasy_medieval": "🛡️",
    "genre_horror_dark": "💀",
    "genre_noir_jazz_blues": "🎷",
    "genre_classical_orchestral": "🎼",
    "genre_rock_alt_indie": "🎸",
    "genre_metal": "⛓️",
    "genre_punk_postpunk": "🧷",
    "genre_folk_acoustic": "🪕",
    "genre_world_ethnic": "🌍",
    "genre_slavic_balkan": "🪗",
    "genre_nordic_pagan": "🪓",
    "genre_middle_eastern": "🕌",
    "genre_asian_japanese_chinese": "🏯",
    "genre_indian_tibetan": "🕉️",
    "genre_latin_afro_caribbean": "💃",
    "genre_retro_vintage": "📻",
    "genre_cartoon_cabaret_circus": "🎪",
    "genre_experimental_noise": "🧪",
    "genre_gothic_darkwave": "🦇",
    "genre_hybrid_modern": "🔀",
}

GENRE_GROUP_LABELS = {
    "genre_rap_general": {"en": "Rap / Hip-Hop", "ru": "Рэп / Хип-хоп"},
    "genre_boom_bap": {"en": "Boom Bap", "ru": "Boom Bap"},
    "genre_trap_drill": {"en": "Trap / Drill", "ru": "Trap / Drill"},
    "genre_phonk_memphis": {"en": "Phonk / Memphis", "ru": "Phonk / Memphis"},
    "genre_cloud_emo_rap": {"en": "Cloud / Emo Rap", "ru": "Cloud / Emo Rap"},
    "genre_rnb_soul": {"en": "R&B / Soul", "ru": "R&B / Soul"},
    "genre_pop": {"en": "Pop", "ru": "Pop"},
    "genre_electronic_general": {"en": "Electronic", "ru": "Electronic"},
    "genre_house": {"en": "House", "ru": "House"},
    "genre_techno": {"en": "Techno", "ru": "Techno"},
    "genre_trance": {"en": "Trance", "ru": "Trance"},
    "genre_dnb_jungle": {"en": "DnB / Jungle", "ru": "DnB / Jungle"},
    "genre_breakbeat_garage": {"en": "Breakbeat / Garage", "ru": "Breakbeat / Garage"},
    "genre_dub_reggae": {"en": "Dub / Reggae", "ru": "Dub / Reggae"},
    "genre_ambient": {"en": "Ambient", "ru": "Ambient"},
    "genre_drone": {"en": "Drone", "ru": "Drone"},
    "genre_lofi_tape": {"en": "Lo-Fi / Tape", "ru": "Lo-Fi / Tape"},
    "genre_cinematic_score": {"en": "Cinematic Score", "ru": "Кинематографичный score"},
    "genre_game_music": {"en": "Game Music", "ru": "Игровая музыка"},
    "genre_fantasy_medieval": {"en": "Fantasy / Medieval", "ru": "Фэнтези / Средневековье"},
    "genre_horror_dark": {"en": "Horror / Dark", "ru": "Хоррор / Тьма"},
    "genre_noir_jazz_blues": {"en": "Noir / Jazz / Blues", "ru": "Нуар / Jazz / Blues"},
    "genre_classical_orchestral": {"en": "Classical / Orchestral", "ru": "Классика / Оркестр"},
    "genre_rock_alt_indie": {"en": "Rock / Alt / Indie", "ru": "Rock / Alt / Indie"},
    "genre_metal": {"en": "Metal", "ru": "Metal"},
    "genre_punk_postpunk": {"en": "Punk / Post-Punk", "ru": "Punk / Post-Punk"},
    "genre_folk_acoustic": {"en": "Folk / Acoustic", "ru": "Folk / Acoustic"},
    "genre_world_ethnic": {"en": "World / Ethnic", "ru": "World / Ethnic"},
    "genre_slavic_balkan": {"en": "Slavic / Balkan", "ru": "Славянское / Балканское"},
    "genre_nordic_pagan": {"en": "Nordic / Pagan", "ru": "Северное / Pagan"},
    "genre_middle_eastern": {"en": "Middle Eastern", "ru": "Ближневосточное"},
    "genre_asian_japanese_chinese": {"en": "Asian / Japanese / Chinese", "ru": "Азиатское / Японское / Китайское"},
    "genre_indian_tibetan": {"en": "Indian / Tibetan", "ru": "Индийское / Тибетское"},
    "genre_latin_afro_caribbean": {"en": "Latin / Afro / Caribbean", "ru": "Латино / Афро / Карибское"},
    "genre_retro_vintage": {"en": "Retro / Vintage", "ru": "Ретро / Винтаж"},
    "genre_cartoon_cabaret_circus": {"en": "Cartoon / Cabaret / Circus", "ru": "Мульт / Кабаре / Цирк"},
    "genre_experimental_noise": {"en": "Experimental / Noise", "ru": "Эксперимент / Noise"},
    "genre_gothic_darkwave": {"en": "Gothic / Darkwave", "ru": "Готика / Darkwave"},
    "genre_hybrid_modern": {"en": "Hybrid Modern", "ru": "Современный гибрид"},
}

GENRE_SEARCH_ALIASES = {
    "hiphop": ["hip-hop", "hip hop", "rap", "рэп", "хип-хоп"],
    "bgm": ["game music", "game soundtrack", "video game", "игровой саундтрек", "музыка видеоигр"],
    "dnb": ["drum and bass", "d&b", "драм энд бэйс"],
    "edm": ["electronic", "dance music", "электроника"],
    "lofi": ["lo-fi", "tape", "cassette", "кассета", "пленка"],
    "noir": ["film noir", "jazz noir", "нуар"],
}


COLLECTIONS = {
    "Dark Fantasy": ["dark fantasy soundtrack", "dark ambient", "long reverb", "deep dark cello", "ritual chanting"],
    "Slavic Ritual": ["slavic folk fusion", "ancient Slavic chanting", "ritual chanting", "dark strings", "old film texture"],
    "VHS Horror": ["cinematic horror", "screeching violins", "tape hiss", "degraded vintage audio", "psychological tension"],
    "Cartoon Noir": ["1960s cartoon noir soundtrack", "jazz noir", "detuned piano", "muted trumpet", "vintage cartoon vibe"],
    "Dungeon Ambient": ["dungeon ambient", "abandoned dungeon", "deep drone", "distant echo", "slow evolving layers"],
    "Berserk Style": ["dark fantasy soundtrack", "tribal drums", "deep dark cello", "tragic", "dissonant harmonies"],
    "Silent Hill Inspired": ["dark ambient", "detuned piano", "tape hiss", "haunting", "empty space"],
    "Soviet Animation": ["1960s cartoon noir soundtrack", "vibraphone", "brush drums", "nostalgic", "old film texture"],
}

GAME_BGM_AUTO_RULES = [
    "loopable structure",
    "non-intrusive background music",
    "low intensity",
    "subtle melodic motif",
    "soft evolving atmosphere",
    "no loud climax",
    "no distracting lead melody",
]

GAME_BGM_QUICK_PRESETS = [
    "Peaceful Fantasy Village",
    "Lonely Border Town",
    "Ancient Forest Exploration",
    "Dark Dungeon Background",
    "Sacred Temple Ambient",
    "Old Tavern Background",
    "War Camp At Night",
    "Forgotten Ruins",
    "Snowy Mountain Pass",
    "Mystic Swamp",
    "Royal Capital Day",
    "Dark Fantasy World Map",
]

GAME_BGM_PRESET_TOKENS = {
    "Peaceful Fantasy Village": [
        "background music",
        "peaceful medieval village",
        "medieval lute",
        "wooden flute",
        "soft strings",
        "subtle percussion",
        "calm",
        "warm and nostalgic",
        "loopable structure",
    ],
    "Lonely Border Town": [
        "game background music",
        "lonely border town",
        "low strings",
        "distant flute",
        "soft frame drum",
        "cold and distant",
        "subtle danger",
        "slow tempo",
    ],
    "Ancient Forest Exploration": [
        "fantasy game soundtrack",
        "ancient forest",
        "bamboo flute",
        "soft choir pads",
        "harp",
        "subtle wind ambience",
        "mysterious",
        "ethereal",
        "seamless loop",
    ],
    "Dark Dungeon Background": [
        "dark dungeon ambient",
        "deep drone",
        "distant echo",
        "low strings",
        "cave ambience",
        "subtle percussion",
        "quiet tension",
        "sparse instrumentation",
        "no vocals",
    ],
    "Sacred Temple Ambient": [
        "sacred temple ambient",
        "ethereal choir",
        "temple bells",
        "duduk",
        "long reverb",
        "ancient stone hall ambience",
        "reverent",
        "mystical",
        "very slow tempo",
    ],
    "Old Tavern Background": [
        "medieval tavern background music",
        "lute",
        "fiddle",
        "bodhran",
        "warm room ambience",
        "calm pacing",
        "subtle melodic motif",
        "loopable fantasy game music",
    ],
    "War Camp At Night": [
        "fantasy war camp background music",
        "distant war drums",
        "low strings",
        "ancient horn",
        "subtle danger",
        "disciplined military mood",
        "night ambience",
        "slow tempo",
    ],
    "Forgotten Ruins": [
        "ancient ruins ambient",
        "deep drone",
        "duduk",
        "soft bells",
        "distant choir",
        "old stone hall ambience",
        "forgotten and old",
        "slow evolving layers",
        "seamless loop",
    ],
    "Snowy Mountain Pass": [
        "snowy mountain ambient",
        "low strings",
        "distant horn",
        "cold airy texture",
        "subtle wind ambience",
        "lonely",
        "majestic",
        "loopable background music",
    ],
    "Mystic Swamp": [
        "foggy swamp ambient",
        "bass clarinet",
        "deep drone",
        "soft percussion",
        "distant ritual voices",
        "wet dark atmosphere",
        "haunting",
        "low intensity",
        "no lyrics",
    ],
    "Royal Capital Day": [
        "fantasy town theme",
        "royal capital",
        "harp",
        "soft strings",
        "French horn",
        "subtle percussion",
        "warm noble atmosphere",
        "andante",
        "non-intrusive background music",
    ],
    "Dark Fantasy World Map": [
        "dark fantasy world map music",
        "low strings",
        "deep cello",
        "distant choir",
        "ancient war horn",
        "cold and solemn",
        "slow evolving layers",
        "cinematic ambient",
        "no lyrics",
    ],
}


class AddTokenDialog(QDialog):
    def __init__(self, categories: List[str], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add token")
        self.resize(480, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.category_combo = QComboBox()
        self.category_combo.addItems(categories)
        self.new_category_input = QLineEdit()
        self.en_input = QLineEdit()
        self.ru_input = QLineEdit()

        form.addRow("Category:", self.category_combo)
        form.addRow("New category:", self.new_category_input)
        form.addRow("English token:", self.en_input)
        form.addRow("Russian translation:", self.ru_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> Dict[str, str]:
        return {
            "category": self.new_category_input.text().strip() or self.category_combo.currentText().strip(),
            "en": self.en_input.text().strip(),
            "ru": self.ru_input.text().strip(),
        }


class AddPromptDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Add prompt")
        self.resize(560, 320)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.prompt_input = QTextEdit()
        self.prompt_input.setMinimumHeight(130)

        form.addRow("Name:", self.name_input)
        form.addRow("Description:", self.description_input)
        form.addRow("Prompt:", self.prompt_input)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def data(self) -> Dict[str, str]:
        return {
            "name": self.name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "prompt": self.prompt_input.toPlainText().strip(),
        }


class TokenCard(QFrame):
    def __init__(self, token: Dict[str, str], on_change, card_size: str = "medium", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.token = token
        self.on_change = on_change
        self.weight = 1.0
        self.active = False
        self.card_size = card_size if card_size in CARD_SIZES else "medium"
        self.setProperty("card", "true")
        self.setProperty("active", "false")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        header = QHBoxLayout()
        self.icon_label = QLabel(self.token.get("icon", "♪"))
        self.icon_label.setStyleSheet("font-size: 20px;")
        self.favorite_button = QPushButton("☆")
        self.favorite_button.setFixedWidth(34)
        self.favorite_button.clicked.connect(self._favorite)

        header.addWidget(self.icon_label)
        header.addStretch()
        layout.addLayout(header)

        self.primary_label = QLabel("")
        self.primary_label.setProperty("cardPrimary", "true")
        self.secondary_label = QLabel("")
        self.secondary_label.setProperty("cardSecondary", "true")
        self.secondary_label.setWordWrap(True)

        layout.addWidget(self.primary_label)
        layout.addWidget(self.secondary_label)

        controls = QHBoxLayout()
        controls.setContentsMargins(4, 0, 4, 0)

        self.minus_button = QPushButton("-")
        self.minus_button.setFixedWidth(30)
        self.minus_button.clicked.connect(self._dec)

        self.weight_label = QLabel("100%")
        self.weight_label.setObjectName("mutedLabel")

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(30)
        self.plus_button.clicked.connect(self._inc)

        controls.addWidget(self.favorite_button)
        controls.addStretch()
        controls.addWidget(self.minus_button)
        controls.addWidget(self.weight_label)
        controls.addWidget(self.plus_button)
        layout.addLayout(controls)

        size = CARD_SIZES[self.card_size]
        self.setMinimumSize(size["width"], size["height"])
        self.setToolTip(self._tooltip_text())

    def _tooltip_text(self) -> str:
        en_text = self.token.get("en", "").strip()
        ru_text = self.token.get("ru", "").strip()
        if ru_text:
            return f"EN: {en_text}\nRU: {ru_text}"
        return f"EN: {en_text}"

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle()
        super().mousePressEvent(event)

    def set_display_text(self, primary: str, secondary: str) -> None:
        self.primary_label.setText(primary)
        self.secondary_label.setText(secondary)
        self.secondary_label.setVisible(bool(secondary))

    def set_active(self, value: bool) -> None:
        self.active = value
        self.setProperty("active", "true" if value else "false")
        self.style().unpolish(self)
        self.style().polish(self)

    def set_favorite(self, value: bool) -> None:
        self.favorite_button.setText("★" if value else "☆")

    def _toggle(self) -> None:
        self.set_active(not self.active)
        self.on_change("toggle", self)

    def _favorite(self) -> None:
        self.on_change("favorite", self)

    def _dec(self) -> None:
        self.weight = max(0.4, round(self.weight - 0.1, 1))
        self.weight_label.setText(f"{int(self.weight * 100)}%")
        self.on_change("weight", self)

    def _inc(self) -> None:
        self.weight = min(1.6, round(self.weight + 0.1, 1))
        self.weight_label.setText(f"{int(self.weight * 100)}%")
        self.on_change("weight", self)


class MainWindow(QMainWindow):
    def __init__(self, base_dir: Path) -> None:
        super().__init__()
        self.storage = Storage(base_dir)
        self.prompt_data = self.storage.load_prompt_data()
        self.presets = self.storage.load_presets()
        self.user_prompts = self.storage.load_user_prompts()
        self.smart_rules = self.storage.load_smart_rules()
        self.settings = self.storage.load_settings() or {}

        self.lang = str(self.settings.get("language", "ru"))
        self.display_mode = str(self.settings.get("display_mode", "both"))
        self.theme = str(self.settings.get("theme", "dark_noir"))
        ui_settings = self.settings.get("ui", {}) if isinstance(self.settings.get("ui", {}), dict) else {}
        self.card_size = str(ui_settings.get("card_size", "medium"))
        self.generator_mode = str(self.settings.get("generator_mode", "default"))
        self.auto_bgm_rules_enabled = bool(self.settings.get("auto_bgm_rules_enabled", True))
        self.structured_mode_enabled = bool(self.settings.get("structured_mode_enabled", False))
        self.favorites = set(self.storage.load_favorites())
        self.recent_token_ids = [str(item) for item in self.settings.get("recent_token_ids", []) if str(item).strip()]
        self.sidebar_collapsed = bool(self.settings.get("ui_layout", {}).get("sidebar_collapsed", False))
        self.prompt_collapsed = bool(self.settings.get("ui_layout", {}).get("prompt_collapsed", False))
        self.smart_collapsed = bool(self.settings.get("ui_layout", {}).get("smart_collapsed", False))
        self.warnings_collapsed = bool(self.settings.get("ui_layout", {}).get("warnings_collapsed", False))
        self.saved_collapsed = bool(self.settings.get("ui_layout", {}).get("saved_collapsed", False))

        self.track_type_category = self._detect_track_type_category()
        self.selected_tokens: Dict[str, Dict[str, Any]] = {}
        self.cards: Dict[str, TokenCard] = {}
        self.active_structure_tags: List[str] = []
        self.active_collection_name: str | None = None
        self.last_smart_action: Dict[str, Any] = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}
        self._all_tokens_cache: List[Dict[str, str]] = []
        self._search_debounce_timer = QTimer(self)
        self._search_debounce_timer.setSingleShot(True)
        self._search_debounce_timer.timeout.connect(self._apply_search_update)
        self.tab_keys = [
            "genres",
            "quality",
            "instruments",
            "vocals",
            "mood",
            "texture",
            "fantasy",
            "horror",
            "hiphop",
            "ambient",
            "game_bgm",
            "favorites",
            "saved",
        ]

        self.setWindowTitle("Suno Prompt Generator")
        self.resize(1360, 860)
        self.setMinimumSize(1180, 760)

        self._rebuild_all_tokens_cache()
        self._build_ui()
        self._apply_language()
        self._apply_theme()
        self._render_cards()
        self.refresh_saved_prompts_table()
        self.update_prompt_preview(animated=False)

    def _build_ui(self) -> None:
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setSpacing(10)

        header = QFrame()
        header.setObjectName("panel")
        header_layout = QHBoxLayout(header)

        self.logo_label = QLabel("♪")
        self.logo_label.setStyleSheet("font-size: 28px; font-weight: 700;")
        self.title_label = QLabel("Suno Prompt Generator")
        self.title_label.setStyleSheet("font-size: 20px; font-weight: 700;")

        self.ru_button = QPushButton("RU")
        self.en_button = QPushButton("EN")
        self.ru_button.clicked.connect(lambda: self.set_language("ru"))
        self.en_button.clicked.connect(lambda: self.set_language("en"))

        self.display_mode_combo = QComboBox()
        self.display_mode_combo.currentIndexChanged.connect(self._on_display_mode_changed)

        self.theme_combo = QComboBox()
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)

        self.card_size_label = QLabel("Card Size")
        self.card_size_combo = QComboBox()
        self.card_size_combo.currentIndexChanged.connect(self._on_card_size_changed)

        header_layout.addWidget(self.logo_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.ru_button)
        header_layout.addWidget(self.en_button)
        header_layout.addWidget(self.display_mode_combo)
        header_layout.addWidget(self.theme_combo)
        header_layout.addWidget(self.card_size_label)
        header_layout.addWidget(self.card_size_combo)
        root_layout.addWidget(header)

        controls = QFrame()
        controls.setObjectName("panel")
        controls_layout = QGridLayout(controls)

        self.track_type_combo = QComboBox()
        self.track_type_combo.currentIndexChanged.connect(self.update_prompt_preview)

        self.preset_combo = QComboBox()
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)

        self.track_type_label = QLabel("Track Type")
        self.preset_label = QLabel("Preset")
        self.collections_label = QLabel("Collections")
        self.generator_mode_label = QLabel("Mode")

        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_summary_label = QLabel("")
        self.search_summary_label.setObjectName("mutedLabel")
        self.quality_hint_label = QLabel("")
        self.quality_hint_label.setObjectName("mutedLabel")
        self.genre_group_filter_label = QLabel("Genre Group")
        self.genre_group_filter_combo = QComboBox()
        self.genre_group_filter_combo.currentIndexChanged.connect(self._on_genre_group_filter_changed)
        self.genre_group_filter_label.setVisible(False)
        self.genre_group_filter_combo.setVisible(False)
        self.quality_group_filter_label = QLabel("Quality Group")
        self.quality_group_filter_combo = QComboBox()
        self.quality_group_filter_combo.currentIndexChanged.connect(self._on_quality_group_filter_changed)
        self.quality_group_filter_label.setVisible(False)
        self.quality_group_filter_combo.setVisible(False)
        self.instrument_group_filter_label = QLabel("Instrument Group")
        self.instrument_group_filter_combo = QComboBox()
        self.instrument_group_filter_combo.currentIndexChanged.connect(self._on_instrument_group_filter_changed)
        self.instrument_group_filter_label.setVisible(False)
        self.instrument_group_filter_combo.setVisible(False)

        self.collection_combo = QComboBox()
        self.collection_combo.addItems(list(COLLECTIONS.keys()))
        self.collection_apply_btn = QPushButton("Apply")
        self.collection_apply_btn.clicked.connect(self.apply_collection)

        self.quality_preset_combo = QComboBox()
        self.quality_apply_btn = QPushButton("Apply")
        self.quality_apply_btn.clicked.connect(self.apply_quality_preset)

        self.filter_selected_only = QCheckBox("Selected only")
        self.filter_favorites_only = QCheckBox("Favorites")
        self.filter_recent_only = QCheckBox("Recently used")
        self.filter_selected_only.toggled.connect(lambda _checked: self._render_cards())
        self.filter_favorites_only.toggled.connect(lambda _checked: self._render_cards())
        self.filter_recent_only.toggled.connect(lambda _checked: self._render_cards())

        self.generator_mode_combo = QComboBox()
        self.generator_mode_combo.currentIndexChanged.connect(self._on_generator_mode_changed)

        self.auto_bgm_rules_btn = QPushButton("Auto BGM Rules")
        self.auto_bgm_rules_btn.setCheckable(True)
        self.auto_bgm_rules_btn.setChecked(self.auto_bgm_rules_enabled)
        self.auto_bgm_rules_btn.clicked.connect(self._on_auto_bgm_rules_toggled)

        self.structured_mode_btn = QPushButton("Structured Mode")
        self.structured_mode_btn.setCheckable(True)
        self.structured_mode_btn.setChecked(self.structured_mode_enabled)
        self.structured_mode_btn.clicked.connect(self._on_structured_mode_toggled)

        self.smart_generate_btn = QPushButton("Smart Generate")
        self.smart_generate_btn.clicked.connect(self.smart_generate)
        self.smart_bgm_btn = QPushButton("Smart BGM")
        self.smart_bgm_btn.clicked.connect(self.smart_bgm_generate)
        self.undo_smart_btn = QPushButton("Undo Smart")
        self.undo_smart_btn.clicked.connect(self.undo_smart)

        self.game_bgm_preset_combo = QComboBox()
        self.game_bgm_preset_combo.addItems(GAME_BGM_QUICK_PRESETS)
        self.game_bgm_apply_btn = QPushButton("Apply")
        self.game_bgm_apply_btn.clicked.connect(self.apply_game_bgm_preset)

        self.import_btn = QPushButton("Import JSON")
        self.import_btn.clicked.connect(self.import_json)
        self.import_pack_btn = QPushButton("Импортировать JSON-пак")
        self.import_pack_btn.clicked.connect(self.import_json_pack)
        self.export_all_btn = QPushButton("Export All")
        self.export_all_btn.clicked.connect(self.export_all_data)
        self.export_tokens_btn = QPushButton("Export Tokens")
        self.export_tokens_btn.clicked.connect(self.export_prompt_data)
        self.export_presets_btn = QPushButton("Export Presets")
        self.export_presets_btn.clicked.connect(self.export_presets)
        self.export_prompts_btn = QPushButton("Export Prompts")
        self.export_prompts_btn.clicked.connect(self.export_user_prompts)

        self.add_word_btn = QPushButton("Add token")
        self.add_word_btn.clicked.connect(self.add_token)
        self.add_prompt_btn = QPushButton("Add prompt")
        self.add_prompt_btn.clicked.connect(self.add_ready_prompt)
        self.save_current_btn = QPushButton("Save current")
        self.save_current_btn.clicked.connect(self.save_current_prompt)
        self.save_preset_btn = QPushButton("Save preset")
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.random_btn = QPushButton("Random")
        self.random_btn.clicked.connect(self.apply_random_selection)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_selection)

        controls_layout.addWidget(self.track_type_label, 0, 0)
        controls_layout.addWidget(self.track_type_combo, 0, 1)
        controls_layout.addWidget(self.preset_label, 0, 2)
        controls_layout.addWidget(self.preset_combo, 0, 3)
        controls_layout.addWidget(self.search_input, 0, 4, 1, 3)
        controls_layout.addWidget(self.instrument_group_filter_label, 0, 7)
        controls_layout.addWidget(self.instrument_group_filter_combo, 0, 8)
        controls_layout.addWidget(self.genre_group_filter_label, 0, 9)
        controls_layout.addWidget(self.genre_group_filter_combo, 0, 10)
        controls_layout.addWidget(self.quality_group_filter_label, 0, 11)
        controls_layout.addWidget(self.quality_group_filter_combo, 0, 12)

        controls_layout.addWidget(self.collections_label, 1, 0)
        controls_layout.addWidget(self.collection_combo, 1, 1)
        controls_layout.addWidget(self.collection_apply_btn, 1, 2)
        controls_layout.addWidget(self.quality_preset_combo, 1, 3)
        controls_layout.addWidget(self.quality_apply_btn, 1, 4)
        controls_layout.addWidget(self.generator_mode_label, 1, 5)
        controls_layout.addWidget(self.generator_mode_combo, 1, 6)
        controls_layout.addWidget(self.auto_bgm_rules_btn, 1, 7)
        controls_layout.addWidget(self.structured_mode_btn, 1, 8)
        controls_layout.addWidget(self.game_bgm_preset_combo, 1, 9)
        controls_layout.addWidget(self.game_bgm_apply_btn, 1, 10)
        controls_layout.addWidget(self.filter_selected_only, 1, 13)
        controls_layout.addWidget(self.filter_favorites_only, 1, 14)
        controls_layout.addWidget(self.filter_recent_only, 1, 15)

        controls_layout.addWidget(self.import_btn, 2, 0)
        controls_layout.addWidget(self.import_pack_btn, 2, 1)
        controls_layout.addWidget(self.export_all_btn, 2, 2)
        controls_layout.addWidget(self.export_tokens_btn, 2, 3)
        controls_layout.addWidget(self.export_presets_btn, 2, 4)
        controls_layout.addWidget(self.export_prompts_btn, 2, 5)

        controls_layout.addWidget(self.add_word_btn, 3, 0)
        controls_layout.addWidget(self.add_prompt_btn, 3, 1)
        controls_layout.addWidget(self.save_current_btn, 3, 2)
        controls_layout.addWidget(self.save_preset_btn, 3, 3)
        controls_layout.addWidget(self.smart_generate_btn, 3, 4)
        controls_layout.addWidget(self.smart_bgm_btn, 3, 5)
        controls_layout.addWidget(self.undo_smart_btn, 3, 6)
        controls_layout.addWidget(self.random_btn, 3, 7)
        controls_layout.addWidget(self.clear_btn, 3, 8)

        root_layout.addWidget(controls)
        root_layout.addWidget(self.search_summary_label)
        root_layout.addWidget(self.quality_hint_label)

        self.tab_bar = QTabBar()
        self.tab_bar.currentChanged.connect(self._on_tab_changed)

        self.sidebar_frame = QFrame()
        self.sidebar_frame.setObjectName("panel")
        self.sidebar_frame.setMinimumWidth(180)
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        self.sidebar_toggle_btn = QPushButton("− Categories")
        self.sidebar_toggle_btn.setCheckable(True)
        self.sidebar_toggle_btn.setChecked(not self.sidebar_collapsed)
        self.sidebar_toggle_btn.clicked.connect(self._toggle_sidebar)
        sidebar_layout.addWidget(self.sidebar_toggle_btn)
        sidebar_layout.addWidget(self.tab_bar)

        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(500)

        self.browser_panel = QFrame()
        self.browser_panel.setObjectName("panel")
        browser_layout = QVBoxLayout(self.browser_panel)
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_container = QWidget()
        self.cards_layout = FlowLayout(self.cards_container, margin=8, hspacing=12, vspacing=12)
        self.cards_scroll.setWidget(self.cards_container)
        browser_layout.addWidget(self.cards_scroll)
        self.stack.addWidget(self.browser_panel)

        self.game_bgm_panel = QFrame()
        self.game_bgm_panel.setObjectName("panel")
        game_bgm_layout = QVBoxLayout(self.game_bgm_panel)

        game_bgm_header = QLabel("Game BGM")
        game_bgm_header.setStyleSheet("font-size: 18px; font-weight: 700;")
        game_bgm_layout.addWidget(game_bgm_header)

        game_bgm_hint = QLabel("Quick presets fill the selection, update the prompt, and can be saved as user prompts.")
        game_bgm_hint.setObjectName("mutedLabel")
        game_bgm_layout.addWidget(game_bgm_hint)

        self.game_bgm_quick_scroll = QScrollArea()
        self.game_bgm_quick_scroll.setWidgetResizable(True)
        self.game_bgm_quick_container = QWidget()
        self.game_bgm_quick_layout = FlowLayout(self.game_bgm_quick_container, margin=8, hspacing=12, vspacing=12)
        self.game_bgm_quick_scroll.setWidget(self.game_bgm_quick_container)
        game_bgm_layout.addWidget(self.game_bgm_quick_scroll)

        self.game_bgm_apply_prompt_btn = QPushButton("Apply selected preset")
        self.game_bgm_apply_prompt_btn.clicked.connect(self.apply_game_bgm_selected_preset)
        game_bgm_layout.addWidget(self.game_bgm_apply_prompt_btn)

        self.stack.addWidget(self.game_bgm_panel)

        self.saved_panel = QFrame()
        self.saved_panel.setObjectName("panel")
        saved_layout = QVBoxLayout(self.saved_panel)
        self.saved_toggle_btn = QPushButton("− Saved Prompts")
        self.saved_toggle_btn.setCheckable(True)
        self.saved_toggle_btn.setChecked(not self.saved_collapsed)
        self.saved_toggle_btn.clicked.connect(self._toggle_saved_panel)
        saved_layout.addWidget(self.saved_toggle_btn)
        self.saved_table = QTableWidget(0, 3)
        self.saved_table.setHorizontalHeaderLabels(["Name", "Date", "Actions"])
        self.saved_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.saved_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.saved_table.verticalHeader().setVisible(False)
        self.saved_table.horizontalHeader().setStretchLastSection(True)
        saved_layout.addWidget(self.saved_table)
        self.stack.addWidget(self.saved_panel)

        self.top_content_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.top_content_splitter.addWidget(self.sidebar_frame)
        self.top_content_splitter.addWidget(self.stack)
        self.top_content_splitter.setChildrenCollapsible(False)

        preview = QFrame()
        preview.setObjectName("panel")
        preview.setMinimumHeight(160)
        preview_layout = QVBoxLayout(preview)

        self.prompt_toggle_btn = QPushButton("− Prompt Preview")
        self.prompt_toggle_btn.setCheckable(True)
        self.prompt_toggle_btn.setChecked(not self.prompt_collapsed)
        self.prompt_toggle_btn.clicked.connect(self._toggle_prompt_panel)
        preview_layout.addWidget(self.prompt_toggle_btn)

        self.preview_title = QLabel("Generated Prompt")
        self.preview_title.setStyleSheet("font-size: 15px; font-weight: 700;")
        preview_layout.addWidget(self.preview_title)

        self.full_toggle_btn = QPushButton("Full Prompt ▾")
        self.full_toggle_btn.setCheckable(True)
        self.full_toggle_btn.setChecked(True)
        self.full_toggle_btn.clicked.connect(lambda checked: self._set_prompt_section_visible("full", checked))
        preview_layout.addWidget(self.full_toggle_btn)

        self.full_prompt_edit = QTextEdit()
        self.full_prompt_edit.setReadOnly(False)
        self.full_prompt_edit.setMinimumHeight(58)
        self._updating_prompt = False
        self.full_prompt_edit.textChanged.connect(self._on_full_prompt_edited)

        self.full_prompt_container = QWidget()
        full_prompt_layout = QVBoxLayout(self.full_prompt_container)
        full_prompt_layout.setContentsMargins(0, 0, 0, 0)
        full_prompt_layout.addWidget(self.full_prompt_edit)
        preview_layout.addWidget(self.full_prompt_container)

        self.short_toggle_btn = QPushButton("Short Prompt (120) ▾")
        self.short_toggle_btn.setCheckable(True)
        self.short_toggle_btn.setChecked(True)
        self.short_toggle_btn.clicked.connect(lambda checked: self._set_prompt_section_visible("short", checked))
        preview_layout.addWidget(self.short_toggle_btn)

        self.short_prompt_edit = QTextEdit()
        self.short_prompt_edit.setReadOnly(True)
        self.short_prompt_edit.setMinimumHeight(46)

        self.short_prompt_container = QWidget()
        short_prompt_layout = QVBoxLayout(self.short_prompt_container)
        short_prompt_layout.setContentsMargins(0, 0, 0, 0)
        short_prompt_layout.addWidget(self.short_prompt_edit)
        preview_layout.addWidget(self.short_prompt_container)

        self.opacity_effect = QGraphicsOpacityEffect(self.full_prompt_edit)
        self.full_prompt_edit.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(240)
        self.fade_anim.setStartValue(0.45)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        metrics = QHBoxLayout()
        self.length_label = QLabel("Length: 0")
        self.length_label.setObjectName("mutedLabel")
        self.complexity_label = QLabel("Complexity: LOW")
        self.complexity_label.setObjectName("mutedLabel")
        self.warning_label = QLabel("")
        self.warning_label.setObjectName("mutedLabel")
        metrics.addWidget(self.length_label)
        metrics.addWidget(self.complexity_label)
        metrics.addWidget(self.warning_label)
        metrics.addStretch()
        preview_layout.addLayout(metrics)

        self.suggestions_label = QLabel("Suggestions: -")
        self.suggestions_label.setObjectName("mutedLabel")
        preview_layout.addWidget(self.suggestions_label)

        actions = QHBoxLayout()
        self.copy_btn = QPushButton("Copy")
        self.copy120_btn = QPushButton("Copy 120")
        self.favorite_prompt_btn = QPushButton("Favorite")
        self.favorite_prompt_btn.setProperty("variant", "accent")
        self.copy_btn.clicked.connect(lambda: self._copy_text(self.full_prompt_edit.toPlainText()))
        self.copy120_btn.clicked.connect(lambda: self._copy_text(self.short_prompt_edit.toPlainText()))
        self.favorite_prompt_btn.clicked.connect(self.save_current_prompt)
        actions.addWidget(self.copy_btn)
        actions.addWidget(self.copy120_btn)
        actions.addWidget(self.favorite_prompt_btn)
        actions.addStretch()
        preview_layout.addLayout(actions)

        self.smart_panel = QFrame()
        self.smart_panel.setObjectName("panel")
        smart_layout = QVBoxLayout(self.smart_panel)
        self.smart_toggle_btn = QPushButton("− Smart Additions")
        self.smart_toggle_btn.setCheckable(True)
        self.smart_toggle_btn.setChecked(not self.smart_collapsed)
        self.smart_toggle_btn.clicked.connect(self._toggle_smart_panel)
        smart_layout.addWidget(self.smart_toggle_btn)
        self.smart_additions_edit = QTextEdit()
        self.smart_additions_edit.setReadOnly(True)
        self.smart_additions_edit.setMinimumHeight(90)
        smart_layout.addWidget(self.smart_additions_edit)

        self.warnings_panel = QFrame()
        self.warnings_panel.setObjectName("panel")
        warnings_layout = QVBoxLayout(self.warnings_panel)
        self.warnings_toggle_btn = QPushButton("− Warnings")
        self.warnings_toggle_btn.setCheckable(True)
        self.warnings_toggle_btn.setChecked(not self.warnings_collapsed)
        self.warnings_toggle_btn.clicked.connect(self._toggle_warnings_panel)
        warnings_layout.addWidget(self.warnings_toggle_btn)
        self.warning_details_edit = QTextEdit()
        self.warning_details_edit.setReadOnly(True)
        self.warning_details_edit.setMinimumHeight(90)
        warnings_layout.addWidget(self.warning_details_edit)

        self.prompt_area_splitter = QSplitter(Qt.Orientation.Vertical)
        self.prompt_area_splitter.addWidget(self.smart_panel)
        self.prompt_area_splitter.addWidget(self.warnings_panel)
        self.prompt_area_splitter.setChildrenCollapsible(False)

        self.bottom_prompt_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.bottom_prompt_splitter.addWidget(preview)
        self.bottom_prompt_splitter.addWidget(self.prompt_area_splitter)
        self.bottom_prompt_splitter.setChildrenCollapsible(False)

        self.main_vertical_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_vertical_splitter.addWidget(self.top_content_splitter)
        self.main_vertical_splitter.addWidget(self.bottom_prompt_splitter)
        self.main_vertical_splitter.setChildrenCollapsible(False)

        root_layout.addWidget(self.main_vertical_splitter, stretch=1)

        self._restore_splitter_state()
        self._toggle_sidebar(self.sidebar_toggle_btn.isChecked())
        self._toggle_prompt_panel(self.prompt_toggle_btn.isChecked())
        self._toggle_smart_panel(self.smart_toggle_btn.isChecked())
        self._toggle_warnings_panel(self.warnings_toggle_btn.isChecked())
        self._toggle_saved_panel(self.saved_toggle_btn.isChecked())

        self._build_game_bgm_quick_presets()
        self._reload_quality_preset_combo()

        self.setCentralWidget(root)

    def _build_game_bgm_quick_presets(self) -> None:
        while self.game_bgm_quick_layout.count():
            item = self.game_bgm_quick_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget is not None:
                widget.deleteLater()

        for preset_name in GAME_BGM_QUICK_PRESETS:
            button = QPushButton(preset_name)
            button.setProperty("card", "true")
            button.setMinimumSize(260, 72)
            button.clicked.connect(lambda checked=False, name=preset_name: self.apply_game_bgm_preset_by_name(name))
            self.game_bgm_quick_layout.addWidget(button)

    def _restore_splitter_state(self) -> None:
        ui_layout = self.settings.get("ui_layout", {}) if isinstance(self.settings, dict) else {}
        if isinstance(ui_layout, dict):
            top_sizes = ui_layout.get("top_content_splitter")
            if isinstance(top_sizes, list) and len(top_sizes) == 2:
                self.top_content_splitter.setSizes([int(top_sizes[0]), int(top_sizes[1])])
            else:
                self.top_content_splitter.setSizes([260, 980])

            main_sizes = ui_layout.get("main_vertical_splitter")
            if isinstance(main_sizes, list) and len(main_sizes) == 2:
                self.main_vertical_splitter.setSizes([int(main_sizes[0]), int(main_sizes[1])])
            else:
                self.main_vertical_splitter.setSizes([620, 240])

            prompt_sizes = ui_layout.get("prompt_area_splitter")
            if isinstance(prompt_sizes, list) and len(prompt_sizes) == 2:
                self.prompt_area_splitter.setSizes([int(prompt_sizes[0]), int(prompt_sizes[1])])
            else:
                self.prompt_area_splitter.setSizes([160, 120])

            bottom_sizes = ui_layout.get("bottom_prompt_splitter")
            if isinstance(bottom_sizes, list) and len(bottom_sizes) == 2:
                self.bottom_prompt_splitter.setSizes([int(bottom_sizes[0]), int(bottom_sizes[1])])
            else:
                self.bottom_prompt_splitter.setSizes([780, 420])

    def _toggle_sidebar(self, expanded: bool) -> None:
        self.tab_bar.setVisible(expanded)
        if expanded:
            current_sizes = self.top_content_splitter.sizes()
            if current_sizes and current_sizes[0] < 180:
                self.top_content_splitter.setSizes([260, max(500, current_sizes[1])])
        else:
            current_sizes = self.top_content_splitter.sizes()
            self.top_content_splitter.setSizes([48, max(500, current_sizes[1] if len(current_sizes) > 1 else 900)])
        if self.lang == "en":
            self.sidebar_toggle_btn.setText("− Categories" if expanded else "+ Categories")
        else:
            self.sidebar_toggle_btn.setText("− Категории" if expanded else "+ Категории")

    def _toggle_prompt_panel(self, expanded: bool) -> None:
        self.preview_title.setVisible(expanded)
        self.full_toggle_btn.setVisible(expanded)
        self.full_prompt_container.setVisible(expanded and self.full_toggle_btn.isChecked())
        self.short_toggle_btn.setVisible(expanded)
        self.short_prompt_container.setVisible(expanded and self.short_toggle_btn.isChecked())
        self.length_label.setVisible(expanded)
        self.complexity_label.setVisible(expanded)
        self.warning_label.setVisible(expanded)
        self.suggestions_label.setVisible(expanded)
        self.copy_btn.setVisible(expanded)
        self.copy120_btn.setVisible(expanded)
        self.favorite_prompt_btn.setVisible(expanded)
        if self.lang == "en":
            self.prompt_toggle_btn.setText("− Prompt Preview" if expanded else "+ Prompt Preview")
        else:
            self.prompt_toggle_btn.setText("− Превью промта" if expanded else "+ Превью промта")

    def _toggle_smart_panel(self, expanded: bool) -> None:
        self.smart_additions_edit.setVisible(expanded)
        if self.lang == "en":
            self.smart_toggle_btn.setText("− Smart Additions" if expanded else "+ Smart Additions")
        else:
            self.smart_toggle_btn.setText("− Smart-добавления" if expanded else "+ Smart-добавления")

    def _toggle_warnings_panel(self, expanded: bool) -> None:
        self.warning_details_edit.setVisible(expanded)
        if self.lang == "en":
            self.warnings_toggle_btn.setText("− Warnings" if expanded else "+ Warnings")
        else:
            self.warnings_toggle_btn.setText("− Предупреждения" if expanded else "+ Предупреждения")

    def _toggle_saved_panel(self, expanded: bool) -> None:
        self.saved_table.setVisible(expanded)
        if self.lang == "en":
            self.saved_toggle_btn.setText("− Saved Prompts" if expanded else "+ Saved Prompts")
        else:
            self.saved_toggle_btn.setText("− Сохраненные промты" if expanded else "+ Сохраненные промты")

    def _reload_quality_preset_combo(self) -> None:
        current = self.quality_preset_combo.currentText().strip()
        presets = self.smart_rules.get("quality_presets", []) if isinstance(self.smart_rules, dict) else []
        self.quality_preset_combo.blockSignals(True)
        self.quality_preset_combo.clear()
        self.quality_preset_combo.addItem("-")
        if isinstance(presets, list):
            for item in presets:
                if not isinstance(item, dict):
                    continue
                en_name = str(item.get("name", "")).strip()
                ru_name = str(item.get("ru", "")).strip()
                if not en_name:
                    continue
                label = en_name if self.lang == "en" or not ru_name else f"{ru_name} / {en_name}"
                self.quality_preset_combo.addItem(label, en_name)
        idx = self.quality_preset_combo.findText(current)
        self.quality_preset_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.quality_preset_combo.blockSignals(False)

    def _on_card_size_changed(self, index: int) -> None:
        self.card_size = str(self.card_size_combo.itemData(index) or "medium")
        if self.card_size not in CARD_SIZES:
            self.card_size = "medium"
        self._persist_settings()
        self._render_cards()

    def _apply_theme(self) -> None:
        self.setStyleSheet(get_stylesheet(self.theme))

    def _set_prompt_section_visible(self, section: str, visible: bool) -> None:
        if section == "full":
            self.full_prompt_container.setVisible(visible)
            self.full_toggle_btn.setText("Full Prompt ▾" if visible else "Full Prompt ▸")
            return
        if section == "short":
            self.short_prompt_container.setVisible(visible)
            self.short_toggle_btn.setText("Short Prompt (120) ▾" if visible else "Short Prompt (120) ▸")

    def _apply_language(self) -> None:
        self.setWindowTitle(t(self.lang, "app_title"))
        self.title_label.setText(t(self.lang, "app_title"))
        self.preview_title.setText(t(self.lang, "generated_prompt"))
        self.track_type_label.setText(t(self.lang, "track_type"))
        self.preset_label.setText(t(self.lang, "preset"))
        self.collections_label.setText(t(self.lang, "collections"))
        self.generator_mode_label.setText("Mode" if self.lang == "en" else "Режим")

        display_items = [
            ("ru", t(self.lang, "russian_only")),
            ("en", t(self.lang, "english_only")),
            ("both", t(self.lang, "both_lang")),
        ]
        current_display = self.display_mode
        self.display_mode_combo.blockSignals(True)
        self.display_mode_combo.clear()
        for key, label in display_items:
            self.display_mode_combo.addItem(label, key)
        idx = max(0, self.display_mode_combo.findData(current_display))
        self.display_mode_combo.setCurrentIndex(idx)
        self.display_mode_combo.blockSignals(False)

        theme_items = [
            ("dark_noir", t(self.lang, "theme_dark_noir")),
            ("blood_ritual", t(self.lang, "theme_blood_ritual")),
            ("cold_ambient", t(self.lang, "theme_cold_ambient")),
            ("fantasy_gold", t(self.lang, "theme_fantasy_gold")),
        ]
        self.theme_combo.blockSignals(True)
        self.theme_combo.clear()
        for key, label in theme_items:
            self.theme_combo.addItem(label, key)
        idx = max(0, self.theme_combo.findData(self.theme))
        self.theme_combo.setCurrentIndex(idx)
        self.theme_combo.blockSignals(False)

        card_size_items = [
            ("small", "Small" if self.lang == "en" else "Маленький"),
            ("medium", "Medium" if self.lang == "en" else "Средний"),
            ("large", "Large" if self.lang == "en" else "Большой"),
        ]
        self.card_size_label.setText(t(self.lang, "card_size"))
        self.card_size_combo.blockSignals(True)
        self.card_size_combo.clear()
        for key, label in card_size_items:
            self.card_size_combo.addItem(label, key)
        card_idx = max(0, self.card_size_combo.findData(self.card_size))
        self.card_size_combo.setCurrentIndex(card_idx)
        self.card_size_combo.blockSignals(False)

        self.search_input.setPlaceholderText(t(self.lang, "search"))
        self.genre_group_filter_label.setText(t(self.lang, "genre_groups"))
        self._refresh_genre_group_filter()
        self.quality_group_filter_label.setText(t(self.lang, "quality_groups"))
        self._refresh_quality_group_filter()
        self.instrument_group_filter_label.setText(t(self.lang, "instrument_groups"))
        self._refresh_instrument_group_filter()
        self.quality_hint_label.setText(
            (
                "These tags guide the mix and mastering character, but do not guarantee real mastering. Use 2-5 quality tags, not the entire list."
                if self.lang == "en"
                else "Эти теги помогают направить характер сведения и мастеринга, но не гарантируют настоящий мастеринг. Для лучшего результата используй 2-5 quality-тегов, а не весь список сразу."
            )
        )
        self.import_btn.setText(t(self.lang, "import_json"))
        self.export_all_btn.setText(t(self.lang, "export_all"))
        self.export_tokens_btn.setText(t(self.lang, "export_tokens"))
        self.export_presets_btn.setText(t(self.lang, "export_presets"))
        self.export_prompts_btn.setText(t(self.lang, "export_prompts"))
        self.add_word_btn.setText(t(self.lang, "add_word"))
        self.add_prompt_btn.setText(t(self.lang, "add_prompt"))
        self.save_current_btn.setText(t(self.lang, "save_current_prompt"))
        self.save_preset_btn.setText(t(self.lang, "save_preset"))
        self.smart_generate_btn.setText(t(self.lang, "smart_generate"))
        self.smart_bgm_btn.setText(t(self.lang, "smart_bgm"))
        self.undo_smart_btn.setText(t(self.lang, "undo_smart"))
        self.random_btn.setText(t(self.lang, "random"))
        self.clear_btn.setText(t(self.lang, "clear"))
        self.copy_btn.setText(t(self.lang, "copy"))
        self.copy120_btn.setText(t(self.lang, "copy120"))
        self.favorite_prompt_btn.setText(t(self.lang, "favorite"))
        self.collection_apply_btn.setText(t(self.lang, "apply"))
        self.quality_apply_btn.setText(t(self.lang, "apply"))
        self.filter_selected_only.setText("Selected only" if self.lang == "en" else "Только выбранные")
        self.filter_favorites_only.setText("Favorites" if self.lang == "en" else "Только избранные")
        self.filter_recent_only.setText("Recently used" if self.lang == "en" else "Недавно использованные")
        self.import_pack_btn.setText("Import JSON pack" if self.lang == "en" else "Импортировать JSON-пак")
        self.structured_mode_btn.setText(t(self.lang, "structured_mode"))
        self.auto_bgm_rules_btn.setText(
            ("Auto BGM Rules: ON" if self.auto_bgm_rules_enabled else "Auto BGM Rules: OFF")
            if self.lang == "en"
            else ("Авто-правила BGM: ВКЛ" if self.auto_bgm_rules_enabled else "Авто-правила BGM: ВЫКЛ")
        )

        mode_items = [
            ("default", "Default" if self.lang == "en" else "Обычный"),
            ("game_background", "Game Background Music" if self.lang == "en" else "Фоновая музыка для игры"),
        ]
        self.generator_mode_combo.blockSignals(True)
        self.generator_mode_combo.clear()
        for key, label in mode_items:
            self.generator_mode_combo.addItem(label, key)
        mode_index = max(0, self.generator_mode_combo.findData(self.generator_mode))
        self.generator_mode_combo.setCurrentIndex(mode_index)
        self.generator_mode_combo.blockSignals(False)
        self._update_search_summary(self.search_input.text().strip())
        self.saved_table.setHorizontalHeaderLabels([
            t(self.lang, "saved_prompts"),
            "Date",
            "Actions",
        ])
        if self.sidebar_toggle_btn.isChecked():
            self.sidebar_toggle_btn.setText("− Categories" if self.lang == "en" else "− Категории")
        else:
            self.sidebar_toggle_btn.setText("+ Categories" if self.lang == "en" else "+ Категории")
        if self.prompt_toggle_btn.isChecked():
            self.prompt_toggle_btn.setText("− Prompt Preview" if self.lang == "en" else "− Превью промта")
        else:
            self.prompt_toggle_btn.setText("+ Prompt Preview" if self.lang == "en" else "+ Превью промта")
        if self.smart_toggle_btn.isChecked():
            self.smart_toggle_btn.setText("− Smart Additions" if self.lang == "en" else "− Smart-добавления")
        else:
            self.smart_toggle_btn.setText("+ Smart Additions" if self.lang == "en" else "+ Smart-добавления")
        if self.warnings_toggle_btn.isChecked():
            self.warnings_toggle_btn.setText("− Warnings" if self.lang == "en" else "− Предупреждения")
        else:
            self.warnings_toggle_btn.setText("+ Warnings" if self.lang == "en" else "+ Предупреждения")
        if self.saved_toggle_btn.isChecked():
            self.saved_toggle_btn.setText("− Saved Prompts" if self.lang == "en" else "− Сохраненные промты")
        else:
            self.saved_toggle_btn.setText("+ Saved Prompts" if self.lang == "en" else "+ Сохраненные промты")
        self._reload_quality_preset_combo()

        self._reload_track_type_combo()
        self._reload_presets_combo()
        self._reload_tab_bar()
        self._render_cards()

    def _reload_tab_bar(self) -> None:
        current = self.tab_bar.currentIndex()
        self.tab_bar.blockSignals(True)
        while self.tab_bar.count() > 0:
            self.tab_bar.removeTab(0)
        labels = {
            "genres": "Genres",
            "quality": (
                "Sound · Quality / Mix / Mastering"
                if self.lang == "en"
                else "Звук · Качество / Сведение / Мастеринг"
            ),
            "instruments": "Instruments",
            "vocals": "Vocals",
            "mood": "Mood",
            "texture": "Texture",
            "fantasy": "Fantasy",
            "horror": "Horror",
            "hiphop": "Hip-Hop",
            "ambient": "Ambient",
            "game_bgm": "Game BGM",
            "favorites": t(self.lang, "favorite"),
            "saved": t(self.lang, "saved"),
        }
        for key in self.tab_keys:
            self.tab_bar.addTab(f"{TAB_ICONS.get(key, '•')} {labels[key]}")
        self.tab_bar.setCurrentIndex(max(0, min(current, self.tab_bar.count() - 1)))
        self.tab_bar.blockSignals(False)
        self._on_tab_changed(self.tab_bar.currentIndex())

    def _reload_track_type_combo(self) -> None:
        values = [token.get("en", "") for token in self.prompt_data.get(self.track_type_category, []) if token.get("en")]
        current = self.track_type_combo.currentText()
        self.track_type_combo.blockSignals(True)
        self.track_type_combo.clear()
        self.track_type_combo.addItems(values)
        if current in values:
            self.track_type_combo.setCurrentText(current)
        elif "instrumental" in values:
            self.track_type_combo.setCurrentText("instrumental")
        elif values:
            self.track_type_combo.setCurrentIndex(0)
        self.track_type_combo.blockSignals(False)

    def _reload_presets_combo(self) -> None:
        current = self.preset_combo.currentText()
        self.preset_combo.blockSignals(True)
        self.preset_combo.clear()
        self.preset_combo.addItem("-")
        self.preset_combo.addItems(list(self.presets.keys()))
        if current and self.preset_combo.findText(current) >= 0:
            self.preset_combo.setCurrentText(current)
        else:
            self.preset_combo.setCurrentIndex(0)
        self.preset_combo.blockSignals(False)

    def _instrument_group_categories(self) -> List[str]:
        groups = [key for key in self.prompt_data.keys() if key.lower().startswith("instrument_")]
        groups.sort(key=lambda key: self._instrument_group_label(key).lower())
        return groups

    def _genre_group_categories(self) -> List[str]:
        groups = [key for key in self.prompt_data.keys() if key.lower().startswith("genre_")]
        groups.sort(key=lambda key: self._genre_group_label(key).lower())
        return groups

    def _quality_group_categories(self) -> List[str]:
        groups = [key for key in self.prompt_data.keys() if key.lower().startswith("quality_")]
        groups.sort(key=lambda key: self._quality_group_label(key).lower())
        return groups

    def _instrument_group_label(self, category: str) -> str:
        labels = INSTRUMENT_GROUP_LABELS.get(category, {})
        if self.lang == "ru":
            if labels.get("ru"):
                return str(labels["ru"])
        else:
            if labels.get("en"):
                return str(labels["en"])
        fallback = category.replace("instrument_", "").replace("_", " ").strip()
        return fallback.title() if fallback else category

    def _genre_group_label(self, category: str) -> str:
        labels = GENRE_GROUP_LABELS.get(category, {})
        if self.lang == "ru":
            if labels.get("ru"):
                return str(labels["ru"])
        else:
            if labels.get("en"):
                return str(labels["en"])
        fallback = category.replace("genre_", "").replace("_", " ").strip()
        return fallback.title() if fallback else category

    def _quality_group_label(self, category: str) -> str:
        labels = QUALITY_GROUP_LABELS.get(category, {})
        if self.lang == "ru":
            if labels.get("ru"):
                return str(labels["ru"])
        else:
            if labels.get("en"):
                return str(labels["en"])
        fallback = category.replace("quality_", "").replace("_", " ").strip()
        return fallback.title() if fallback else category

    def _refresh_instrument_group_filter(self) -> None:
        current_group = str(self.instrument_group_filter_combo.currentData() or "all")
        self.instrument_group_filter_combo.blockSignals(True)
        self.instrument_group_filter_combo.clear()
        self.instrument_group_filter_combo.addItem(t(self.lang, "all_instruments"), "all")
        for category in self._instrument_group_categories():
            icon = INSTRUMENT_GROUP_ICONS.get(category, "🎻")
            self.instrument_group_filter_combo.addItem(f"{icon} {self._instrument_group_label(category)}", category)
        idx = self.instrument_group_filter_combo.findData(current_group)
        self.instrument_group_filter_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.instrument_group_filter_combo.blockSignals(False)

    def _refresh_genre_group_filter(self) -> None:
        current_group = str(self.genre_group_filter_combo.currentData() or "all")
        self.genre_group_filter_combo.blockSignals(True)
        self.genre_group_filter_combo.clear()
        self.genre_group_filter_combo.addItem(t(self.lang, "all_genres"), "all")
        for category in self._genre_group_categories():
            icon = GENRE_GROUP_ICONS.get(category, "🎼")
            self.genre_group_filter_combo.addItem(f"{icon} {self._genre_group_label(category)}", category)
        idx = self.genre_group_filter_combo.findData(current_group)
        self.genre_group_filter_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.genre_group_filter_combo.blockSignals(False)

    def _refresh_quality_group_filter(self) -> None:
        current_group = str(self.quality_group_filter_combo.currentData() or "all")
        self.quality_group_filter_combo.blockSignals(True)
        self.quality_group_filter_combo.clear()
        self.quality_group_filter_combo.addItem(t(self.lang, "all_quality"), "all")
        for category in self._quality_group_categories():
            self.quality_group_filter_combo.addItem(f"🎚️ {self._quality_group_label(category)}", category)
        idx = self.quality_group_filter_combo.findData(current_group)
        self.quality_group_filter_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.quality_group_filter_combo.blockSignals(False)

    def _on_instrument_group_filter_changed(self, _index: int) -> None:
        self._render_cards()

    def _on_genre_group_filter_changed(self, _index: int) -> None:
        self._render_cards()

    def _on_quality_group_filter_changed(self, _index: int) -> None:
        self._render_cards()

    def apply_quality_preset(self) -> None:
        selected_name = str(self.quality_preset_combo.currentData() or "").strip()
        if not selected_name:
            return
        presets = self.smart_rules.get("quality_presets", []) if isinstance(self.smart_rules, dict) else []
        if not isinstance(presets, list):
            return

        for preset in presets:
            if not isinstance(preset, dict):
                continue
            if str(preset.get("name", "")).strip().lower() != selected_name.lower():
                continue
            tokens = [str(token).strip() for token in preset.get("tokens", []) if str(token).strip()]
            if not tokens:
                return
            lower_set = {token.lower() for token in tokens}
            for token in self._all_tokens():
                if token["en"].lower() in lower_set:
                    self.selected_tokens[token["id"]] = {
                        "category": token["category"],
                        "en": token["en"],
                        "weight": 1.0,
                    }
            self._render_cards()
            self.update_prompt_preview()
            return

    def _display_name(self, token: Dict[str, str]) -> str:
        en_text = token.get("en", "")
        ru_text = token.get("ru", "")
        if self.display_mode == "en":
            return en_text
        if self.display_mode == "ru":
            return ru_text or en_text
        if ru_text:
            return f"{ru_text}\n{en_text}"
        return en_text

    def _display_pair(self, token: Dict[str, str]) -> tuple[str, str]:
        en_text = token.get("en", "")
        ru_text = token.get("ru", "")
        if self.display_mode == "en":
            return en_text, ru_text
        if self.display_mode == "ru":
            return (ru_text or en_text), en_text if ru_text else ""
        if self.lang == "en":
            return en_text, ru_text
        return (ru_text or en_text), en_text if ru_text else ""

    def _token_id(self, category: str, en_value: str) -> str:
        return f"{category.lower()}::{en_value.strip().lower()}"

    def _category_icon(self, category: str, en_value: str) -> str:
        c = category.lower()
        v = en_value.lower()
        if c.startswith("quality_"):
            return "🎚️"
        if category in GENRE_GROUP_ICONS:
            return GENRE_GROUP_ICONS[category]
        if category in INSTRUMENT_GROUP_ICONS:
            return INSTRUMENT_GROUP_ICONS[category]
        if "instrument" in c or "инстру" in c:
            return "🎻"
        if "vocal" in c or "вок" in c:
            return "🗣"
        if "mood" in c or "настро" in c:
            return "🌙"
        if "texture" in c or "текстур" in c:
            return "🌫"
        if "hip" in v or "bap" in v or "trap" in v:
            return "🎛"
        if "horror" in v:
            return "💀"
        if "ambient" in v:
            return "🌌"
        if "fantasy" in v:
            return "🛡"
        return "♪"

    def _all_tokens(self) -> List[Dict[str, str]]:
        return self._all_tokens_cache

    def _rebuild_all_tokens_cache(self) -> None:
        tokens: List[Dict[str, str]] = []
        for category, items in self.prompt_data.items():
            if category == self.track_type_category:
                continue
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                en_value = str(item.get("en", "")).strip()
                if not en_value:
                    continue
                token = {
                    "category": category,
                    "en": en_value,
                    "ru": str(item.get("ru", "")).strip(),
                    "id": self._token_id(category, en_value),
                    "icon": self._category_icon(category, en_value),
                }
                tokens.append(token)
        self._all_tokens_cache = tokens

    def _token_in_tab(self, token: Dict[str, str], tab_key: str) -> bool:
        category = token.get("category", "").lower()
        en_text = token.get("en", "").lower()
        ru_text = token.get("ru", "").lower()

        def has(*words: str) -> bool:
            return any(w in category or w in en_text or w in ru_text for w in words)

        if tab_key == "favorites":
            return token["id"] in self.favorites
        if tab_key == "genres":
            return category.startswith("genre_") or has("жанр", "genre", "genres")
        if tab_key == "quality":
            return category.startswith("quality_") or has("quality", "mix", "master", "eq", "stereo", "reverb")
        if tab_key == "instruments":
            return has("инстру", "instrument")
        if tab_key == "vocals":
            return has("вок", "vocal", "chant", "choir", "negative_tags")
        if tab_key == "mood":
            return has("настро", "mood")
        if tab_key == "texture":
            return has("текстур", "texture", "reverb", "echo")
        if tab_key == "fantasy":
            return has("fantasy", "medieval", "dungeon", "slavic", "ritual")
        if tab_key == "horror":
            return has("horror", "sinister", "eerie", "haunting")
        if tab_key == "hiphop":
            return has("hip-hop", "boom bap", "trap", "phonk", "scratches")
        if tab_key == "ambient":
            return has("ambient", "atmosphere", "drone")
        if tab_key == "game_bgm":
            return has(
                "game",
                "background",
                "fantasy",
                "location",
                "village",
                "town",
                "dungeon",
                "temple",
                "ambient",
                "loopable",
            )
        return True

    def _render_cards(self) -> None:
        if self.current_tab_key() == "saved":
            return

        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget() if item else None
            if widget is not None:
                widget.deleteLater()

        self.cards = {}
        query = self.search_input.text().strip().lower()
        selected_group = str(self.instrument_group_filter_combo.currentData() or "all")
        selected_genre_group = str(self.genre_group_filter_combo.currentData() or "all")
        selected_quality_group = str(self.quality_group_filter_combo.currentData() or "all")

        for token in self._all_tokens():
            if not self._token_in_tab(token, self.current_tab_key()):
                continue
            if self.current_tab_key() == "instruments" and selected_group != "all":
                if token.get("category") != selected_group:
                    continue
            if self.current_tab_key() == "genres" and selected_genre_group != "all":
                if token.get("category") != selected_genre_group:
                    continue
            if self.current_tab_key() == "quality" and selected_quality_group != "all":
                if token.get("category") != selected_quality_group:
                    continue
            if self.filter_selected_only.isChecked() and token["id"] not in self.selected_tokens:
                continue
            if self.filter_favorites_only.isChecked() and token["id"] not in self.favorites:
                continue
            if self.filter_recent_only.isChecked() and token["id"] not in set(self.recent_token_ids[:80]):
                continue
            if query and not self._token_matches_search(token, query):
                continue

            card = TokenCard(token, self._on_card_action, card_size=self.card_size)
            primary, secondary = self._display_pair(token)
            card.set_display_text(primary, secondary)
            card.set_favorite(token["id"] in self.favorites)

            selected = self.selected_tokens.get(token["id"])
            if selected:
                card.weight = float(selected.get("weight", 1.0))
                card.weight_label.setText(f"{int(card.weight * 100)}%")
                card.set_active(True)

            self.cards_layout.addWidget(card)
            self.cards[token["id"]] = card

    def current_tab_key(self) -> str:
        idx = self.tab_bar.currentIndex()
        if idx < 0 or idx >= len(self.tab_keys):
            return "genres"
        return self.tab_keys[idx]

    def _on_tab_changed(self, index: int) -> None:
        _ = index
        current_tab = self.current_tab_key()
        show_instrument_filter = current_tab == "instruments"
        show_genre_filter = current_tab == "genres"
        show_quality_filter = current_tab == "quality"
        show_large_filters = current_tab in {"genres", "instruments", "quality"}
        self.instrument_group_filter_label.setVisible(show_instrument_filter)
        self.instrument_group_filter_combo.setVisible(show_instrument_filter)
        self.genre_group_filter_label.setVisible(show_genre_filter)
        self.genre_group_filter_combo.setVisible(show_genre_filter)
        self.quality_group_filter_label.setVisible(show_quality_filter)
        self.quality_group_filter_combo.setVisible(show_quality_filter)
        self.quality_hint_label.setVisible(show_quality_filter)
        self.filter_selected_only.setVisible(show_large_filters)
        self.filter_favorites_only.setVisible(show_large_filters)
        self.filter_recent_only.setVisible(show_large_filters)
        if current_tab == "saved":
            self.stack.setCurrentWidget(self.saved_panel)
            self.refresh_saved_prompts_table()
        elif current_tab == "game_bgm":
            self.stack.setCurrentWidget(self.game_bgm_panel)
            if self.generator_mode != "game_background":
                self.generator_mode = "game_background"
                self._persist_settings()
                self._apply_language()
            self.update_prompt_preview()
        else:
            self.stack.setCurrentWidget(self.browser_panel)
            self._render_cards()

    def _on_card_action(self, action: str, card: TokenCard) -> None:
        token = card.token
        token_id = token["id"]

        if action == "favorite":
            if token_id in self.favorites:
                self.favorites.remove(token_id)
            else:
                self.favorites.add(token_id)
            self.storage.save_favorites(sorted(self.favorites))
            card.set_favorite(token_id in self.favorites)
            if self.current_tab_key() == "favorites":
                self._render_cards()
            return

        if action == "toggle":
            if card.active:
                self.selected_tokens[token_id] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": card.weight,
                }
                if token_id in self.recent_token_ids:
                    self.recent_token_ids.remove(token_id)
                self.recent_token_ids.insert(0, token_id)
                self.recent_token_ids = self.recent_token_ids[:200]
            else:
                self.selected_tokens.pop(token_id, None)

        if action == "weight" and token_id in self.selected_tokens:
            self.selected_tokens[token_id]["weight"] = card.weight

        self.update_prompt_preview()

    def _assemble_prompt_parts(self) -> List[str]:
        parts: List[str] = []
        seen: set[str] = set()

        track_type = self.track_type_combo.currentText().strip()
        if track_type:
            parts.append(track_type)
            seen.add(track_type.lower())

        for tag in self.active_structure_tags:
            normalized_tag = str(tag).strip()
            if not normalized_tag:
                continue
            if normalized_tag.lower() in seen:
                continue
            parts.append(normalized_tag)
            seen.add(normalized_tag.lower())

        ordered_categories = [key for key in self.prompt_data.keys() if key != self.track_type_category]
        selected_by_cat: Dict[str, List[Dict[str, Any]]] = {}
        for item in self.selected_tokens.values():
            selected_by_cat.setdefault(item["category"], []).append(item)

        for category in ordered_categories:
            category_items = selected_by_cat.get(category, [])
            category_order = [
                str(token.get("en", "")).strip()
                for token in self.prompt_data.get(category, [])
                if isinstance(token, dict) and str(token.get("en", "")).strip()
            ]
            order_index = {value.lower(): idx for idx, value in enumerate(category_order)}
            category_items.sort(key=lambda item: order_index.get(item["en"].lower(), 9999))

            for item in category_items:
                en_token = item["en"].strip()
                if not en_token:
                    continue
                if category.lower() == "quality_structured_meta_tags" and not self.structured_mode_enabled:
                    continue
                if en_token.lower() == "no vocals":
                    continue
                if en_token.lower() in seen:
                    continue
                seen.add(en_token.lower())
                weight = float(item.get("weight", 1.0))
                if abs(weight - 1.0) > 0.05:
                    parts.append(f"{en_token}:{weight:.1f}")
                else:
                    parts.append(en_token)

        if self.generator_mode == "game_background" and self.auto_bgm_rules_enabled:
            for rule in GAME_BGM_AUTO_RULES:
                if rule.lower() not in seen:
                    parts.append(rule)
                    seen.add(rule.lower())
        return parts

    def update_prompt_preview(self, animated: bool = True) -> None:
        parts = self._assemble_prompt_parts()
        full_prompt = ", ".join(parts)
        short_prompt = build_short_prompt(parts, max_length=120)

        self._updating_prompt = True
        self.full_prompt_edit.setPlainText(full_prompt)
        self.short_prompt_edit.setPlainText(short_prompt)
        self._updating_prompt = False

        self._update_preview_metrics(full_prompt, short_prompt, len(self.selected_tokens))

        if animated:
            self.fade_anim.stop()
            self.fade_anim.start()

    def _update_preview_metrics(self, full_prompt: str, short_prompt: str, selected_count: int) -> None:

        prompt_len = len(full_prompt)
        if selected_count < 5:
            complexity = "LOW"
        elif selected_count < 10:
            complexity = "MEDIUM"
        else:
            complexity = "HIGH"

        warning = ""
        instrument_count = self._count_selected_instruments()
        genre_count = self._count_selected_genres()
        quality_count = self._count_selected_quality()
        quality_limits = self.smart_rules.get("quality_limits", {}) if isinstance(self.smart_rules, dict) else {}
        quality_warn_limit = int(quality_limits.get("warn_if_more_than", 6)) if isinstance(quality_limits, dict) else 6
        quality_per_group_limit = int(quality_limits.get("max_quality_tokens_per_group", 2)) if isinstance(quality_limits, dict) else 2
        quality_per_group_exceeded = any(count > quality_per_group_limit for count in self._selected_quality_group_counts().values())
        if genre_count > 4:
            warning = (
                "Слишком много жанров. Suno может размыть стиль. Лучше оставить 1-3 жанра."
                if self.lang == "ru"
                else "Too many genres. Suno may blur the style. Keep 1-3 genres."
            )
        elif quality_count > quality_warn_limit or quality_per_group_exceeded:
            warning = (
                "Слишком много quality/mastering тегов. Suno может усреднить результат. Лучше выбрать 2-5 самых важных."
                if self.lang == "ru"
                else "Too many quality/mastering tags. Suno may average the result. Choose 2-5 key tags."
            )
        elif instrument_count > 6:
            warning = (
                "Слишком много инструментов. Suno может смешать их неразборчиво. Лучше оставить 3-6 главных инструментов."
                if self.lang == "ru"
                else "Too many instruments. Suno may blend them unclearly. Keep 3-6 main instruments."
            )
        elif prompt_len > 280:
            warning = "Prompt may be overloaded"

        self.length_label.setText(f"{t(self.lang, 'length')}: {prompt_len}")
        self.complexity_label.setText(f"{t(self.lang, 'complexity')}: {complexity}")
        self.warning_label.setText(f"{t(self.lang, 'warning')}: {warning}" if warning else "")
        self.warning_details_edit.setPlainText(warning)

        self.suggestions_label.setText(f"{t(self.lang, 'suggestions')}: {self._build_suggestions_text()}")

    def _on_full_prompt_edited(self) -> None:
        if self._updating_prompt:
            return
        full_prompt = self.full_prompt_edit.toPlainText().strip()
        parts = [part.strip() for part in full_prompt.split(",") if part.strip()]
        short_prompt = build_short_prompt(parts, max_length=120)
        self.short_prompt_edit.setPlainText(short_prompt)
        self._update_preview_metrics(full_prompt, short_prompt, len(parts))

    def _count_in_category_keywords(self, keyword: str) -> int:
        result = 0
        for item in self.selected_tokens.values():
            if keyword in item["category"].lower() or keyword in item["en"].lower():
                result += 1
        return result

    def _count_selected_instruments(self) -> int:
        count = 0
        for item in self.selected_tokens.values():
            category = str(item.get("category", "")).lower()
            if category.startswith("instrument_") or "instrument" in category or "инстру" in category:
                count += 1
        return count

    def _count_selected_genres(self) -> int:
        count = 0
        for item in self.selected_tokens.values():
            category = str(item.get("category", "")).lower()
            if category.startswith("genre_") or "genre" in category or "жанр" in category:
                count += 1
        return count

    def _count_selected_quality(self) -> int:
        count = 0
        for item in self.selected_tokens.values():
            category = str(item.get("category", "")).lower()
            if category.startswith("quality_") or "quality" in category:
                count += 1
        return count

    def _selected_quality_group_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in self.selected_tokens.values():
            category = str(item.get("category", "")).lower()
            if category.startswith("quality_"):
                counts[category] = counts.get(category, 0) + 1
        return counts

    def _build_suggestions_text(self) -> str:
        selected_en = {item["en"].lower() for item in self.selected_tokens.values()}
        suggestion_map = {
            "dark ambient": ["deep drone", "distant choir", "long reverb"],
            "ritual chanting": ["shamanic frame drum", "distant echo"],
            "jazz noir": ["muted trumpet", "vibraphone"],
            "slavic folk fusion": ["ancient Slavic chanting", "dark strings"],
        }
        suggested: List[str] = []
        for key, values in suggestion_map.items():
            if key in selected_en:
                for value in values:
                    if value not in selected_en and value not in suggested:
                        suggested.append(value)
        return ", ".join(suggested[:4]) if suggested else "-"

    def _copy_text(self, text: str) -> None:
        value = text.strip()
        if not value:
            return
        QApplication.clipboard().setText(value)
        self.statusBar().showMessage("Copied", 1500)

    def _on_display_mode_changed(self, index: int) -> None:
        self.display_mode = str(self.display_mode_combo.itemData(index))
        self._persist_settings()
        self._render_cards()

    def _on_theme_changed(self, index: int) -> None:
        self.theme = str(self.theme_combo.itemData(index))
        self._persist_settings()
        self._apply_theme()
        self._render_cards()

    def _on_generator_mode_changed(self, index: int) -> None:
        self.generator_mode = str(self.generator_mode_combo.itemData(index))
        self._persist_settings()
        self.update_prompt_preview()

    def _on_auto_bgm_rules_toggled(self, checked: bool) -> None:
        self.auto_bgm_rules_enabled = checked
        self._persist_settings()
        self._apply_language()
        self.update_prompt_preview()

    def _on_structured_mode_toggled(self, checked: bool) -> None:
        self.structured_mode_enabled = checked
        self._persist_settings()
        self._apply_language()

    def _on_search_changed(self) -> None:
        self._search_debounce_timer.start(120)

    def _apply_search_update(self) -> None:
        self._render_cards()
        self._update_search_summary(self.search_input.text().strip())

    def _update_search_summary(self, query: str) -> None:
        if not query:
            self.search_summary_label.setText("")
            return
        found = self._search_summary(query)
        self.search_summary_label.setText(found)

    def _search_summary(self, query: str) -> str:
        query_lower = query.lower().strip()
        if not query_lower:
            return ""

        categories: List[str] = []
        rule_hits: List[str] = []
        prompt_hits: List[str] = []

        for token in self._all_tokens():
            if query_lower in token["en"].lower() or query_lower in token.get("ru", "").lower():
                categories.append(self._group_label(token["category"]))
                continue
            category_label = self._group_label(token["category"]).lower()
            if query_lower in token["category"].lower() or query_lower in category_label:
                categories.append(self._group_label(token["category"]))

        smart_rules_text = self._smart_rules_search_text()
        if query_lower in smart_rules_text:
            rule_hits.append("Smart Rules")

        for prompt in self.user_prompts:
            prompt_text = f"{prompt.get('name', '')} {prompt.get('prompt', '')} {prompt.get('description', '')}".lower()
            if query_lower in prompt_text:
                prompt_hits.append(str(prompt.get("name", "Untitled")))

        categories_text = ", ".join(sorted(set(categories))) if categories else "-"
        rules_text = ", ".join(rule_hits[:4]) if rule_hits else "-"
        prompts_text = ", ".join(prompt_hits[:4]) if prompt_hits else "-"
        return f"Found in: {categories_text} | Rules: {rules_text} | Prompts: {prompts_text}"

    def _group_label(self, category: str) -> str:
        if category.lower().startswith("instrument_"):
            return self._instrument_group_label(category)
        if category.lower().startswith("genre_"):
            return self._genre_group_label(category)
        if category.lower().startswith("quality_"):
            return self._quality_group_label(category)
        return category.replace("_", " ").title()

    def _smart_rules_search_text(self) -> str:
        parts: List[str] = []
        for section_name, section_value in self.smart_rules.items():
            if isinstance(section_value, dict):
                parts.append(section_name)
                for rule_name, payload in section_value.items():
                    parts.append(str(rule_name))
                    if isinstance(payload, dict):
                        parts.extend(str(item) for item in payload.get("add", []))
                        parts.extend(str(item) for item in payload.get("avoid", []))
            elif isinstance(section_value, list):
                for item in section_value:
                    if isinstance(item, dict):
                        parts.extend(str(value) for value in item.values())
        return " | ".join(parts).lower()

    def _token_matches_search(self, token: Dict[str, str], query: str) -> bool:
        query_lower = query.lower().strip()
        if not query_lower:
            return True
        if query_lower in token["en"].lower() or query_lower in token.get("ru", "").lower():
            return True

        category_key = str(token.get("category", ""))
        category_label = self._group_label(category_key)
        if query_lower in category_key.lower() or query_lower in category_label.lower():
            return True
        alias_terms = GENRE_SEARCH_ALIASES.get(query_lower)
        if alias_terms:
            en_text = token["en"].lower()
            ru_text = token.get("ru", "").lower()
            category_low = category_key.lower()
            category_label_low = category_label.lower()
            for term in alias_terms:
                t_low = term.lower()
                if t_low in en_text or t_low in ru_text or t_low in category_low or t_low in category_label_low:
                    return True
        return False

    def _smart_result_message(self, result: Dict[str, Any]) -> str:
        is_ru = self.lang == "ru"
        additions = result.get("explanations", []) or []
        warnings = result.get("warnings", []) or []
        lines: List[str] = []
        lines.append("Умно добавлено:" if is_ru else "Smart additions:")

        if additions:
            for item in additions:
                token = str(item.get("token", "")).strip()
                reason = str(item.get("reason_ru", "") if is_ru else item.get("reason_en", "")).strip()
                if token:
                    lines.append(f"+ {token} — {reason}" if reason else f"+ {token}")
        else:
            lines.append("-" if is_ru else "-")

        if warnings:
            lines.append("")
            lines.append("Предупреждения:" if is_ru else "Warnings:")
            for item in warnings:
                message = str(item.get("message_ru", "") if is_ru else item.get("message_en", "")).strip()
                if message:
                    lines.append(f"- {message}")

        if result.get("reason"):
            lines.append("")
            lines.append(str(result.get("reason")))
        return "\n".join(lines).strip()

    def _run_smart_generation(self, app_mode: str) -> None:
        selected_tokens = [str(item.get("en", "")).strip() for item in self.selected_tokens.values() if str(item.get("en", "")).strip()]
        result = smart_generate_prompt(
            selected_tokens,
            self.prompt_data,
            self.smart_rules,
            app_mode=app_mode,
            active_collection=self.active_collection_name,
            structured_mode=self.structured_mode_enabled,
        )

        added_tokens = [str(token).strip() for token in result.get("added_tokens", []) if str(token).strip()]
        structure_tags = [str(token).strip() for token in result.get("structure_tags", []) if str(token).strip()]
        token_lookup = {token["en"].lower(): token for token in self._all_tokens()}

        added_ids: List[str] = []
        existing_ids = set(self.selected_tokens.keys())
        for token_text in added_tokens:
            token = token_lookup.get(token_text.lower())
            if not token:
                continue
            token_id = token["id"]
            if token_id in self.selected_tokens:
                continue
            self.selected_tokens[token_id] = {
                "category": token["category"],
                "en": token["en"],
                "weight": 1.0,
            }
            added_ids.append(token_id)

        self.active_structure_tags = structure_tags
        self.last_smart_action = {
            "added_tokens": added_ids,
            "structure_tags": structure_tags,
            "mode": app_mode,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

        self._render_cards()
        self.update_prompt_preview()

        message = self._smart_result_message(result)
        self.smart_additions_edit.setPlainText(message)
        warning_lines = []
        for item in result.get("warnings", []) or []:
            warning_text = str(item.get("message_ru", "") if self.lang == "ru" else item.get("message_en", "")).strip()
            if warning_text:
                warning_lines.append(warning_text)
        self.warning_details_edit.setPlainText("\n".join(warning_lines))
        self.statusBar().showMessage(str(result.get("reason", "Smart generation completed.")), 3500)
        QMessageBox.information(self, "Smart Generate", message or str(result.get("reason", "Smart generation completed.")))

    def smart_generate(self) -> None:
        self._run_smart_generation("general")

    def smart_bgm_generate(self) -> None:
        self._run_smart_generation("smart_bgm")

    def undo_smart(self) -> None:
        last_added = self.last_smart_action.get("added_tokens", []) if isinstance(self.last_smart_action, dict) else []
        last_tags = self.last_smart_action.get("structure_tags", []) if isinstance(self.last_smart_action, dict) else []

        if not last_added and not last_tags:
            return

        for token_id in list(last_added):
            self.selected_tokens.pop(str(token_id), None)

        if last_tags:
            last_tag_set = {str(tag).strip().lower() for tag in last_tags if str(tag).strip()}
            self.active_structure_tags = [tag for tag in self.active_structure_tags if tag.lower() not in last_tag_set]

        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}
        self._render_cards()
        self.update_prompt_preview()
        self.smart_additions_edit.clear()
        self.statusBar().showMessage("Smart additions removed", 2500)

    def apply_game_bgm_preset(self) -> None:
        preset_name = self.game_bgm_preset_combo.currentText().strip()
        if not preset_name:
            return
        for item in self.user_prompts:
            if item.get("name", "").strip().lower() == preset_name.lower():
                self._apply_prompt_to_selection(item.get("prompt", ""))
                return
        QMessageBox.information(self, "Info", "Preset prompt not found in user prompts.")

    def apply_game_bgm_selected_preset(self) -> None:
        if not self.game_bgm_quick_layout.count():
            return
        current_button = self.sender()
        if not isinstance(current_button, QPushButton):
            return
        self.apply_game_bgm_preset_by_name(current_button.text())

    def apply_game_bgm_preset_by_name(self, preset_name: str) -> None:
        tokens = GAME_BGM_PRESET_TOKENS.get(preset_name)
        if not tokens:
            return

        self.active_collection_name = None
        self.active_structure_tags = []
        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}

        if self.track_type_combo.findText("background music") >= 0:
            self.track_type_combo.setCurrentText("background music")
        elif self.track_type_combo.count() > 0:
            self.track_type_combo.setCurrentIndex(0)

        self.selected_tokens = {}
        lower_tokens = {token.lower() for token in tokens}

        for token in self._all_tokens():
            if token["en"].lower() in lower_tokens:
                self.selected_tokens[token["id"]] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": 1.0,
                }

        prompt_text = ", ".join(tokens)
        self._render_cards()
        self._updating_prompt = True
        self.full_prompt_edit.setPlainText(prompt_text)
        short_prompt = build_short_prompt(tokens, max_length=120)
        self.short_prompt_edit.setPlainText(short_prompt)
        self._updating_prompt = False
        self._update_preview_metrics(prompt_text, short_prompt, len(self.selected_tokens))
        self.tab_bar.setCurrentIndex(self.tab_keys.index("game_bgm"))
        self.update_prompt_preview()

    def _apply_prompt_to_selection(self, prompt_text: str) -> None:
        cleaned = [part.strip() for part in prompt_text.split(",") if part.strip()]
        if not cleaned:
            return

        track_types = {token.get("en", "") for token in self.prompt_data.get(self.track_type_category, []) if isinstance(token, dict)}
        self.clear_selection()
        self.active_collection_name = None
        self.active_structure_tags = []
        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}

        for part in cleaned:
            token = part.split(":", 1)[0].strip()
            if token in track_types:
                self.track_type_combo.setCurrentText(token)
                continue
            for item in self._all_tokens():
                if item.get("en", "").lower() == token.lower():
                    self.selected_tokens[item["id"]] = {
                        "category": item["category"],
                        "en": item["en"],
                        "weight": 1.0,
                    }
                    break

        self._render_cards()
        self._updating_prompt = True
        self.full_prompt_edit.setPlainText(prompt_text.strip())
        short_prompt = build_short_prompt(cleaned, max_length=120)
        self.short_prompt_edit.setPlainText(short_prompt)
        self._updating_prompt = False
        self._update_preview_metrics(prompt_text.strip(), short_prompt, len(cleaned))

    def import_json_pack(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Import JSON pack",
            str(self.storage.base_dir),
            "JSON Files (*.json)",
        )
        if not file_name:
            return

        try:
            raw = load_json_file(Path(file_name))
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "JSON повреждён. Импорт отменён.")
            return
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Error", f"Read error: {exc}")
            return

        if not isinstance(raw, dict):
            QMessageBox.warning(self, "Error", "Файл JSON распознан, но структура не подходит для импорта.")
            return

        token_payload: Dict[str, Any] = {}
        ready_prompts_payload: List[Dict[str, str]] = []
        smart_rules_payload: Dict[str, Any] = {}

        for key, value in raw.items():
            if key in {"meta", "generator_modes"}:
                continue
            if key == "smart_rules" and isinstance(value, dict):
                smart_rules_payload = value
                continue
            if key in {"global_rules", "mode_rules", "genre_rules", "mood_rules", "instrument_rules", "vocal_rules", "texture_rules", "performance_rules", "collection_rules", "conflict_rules", "smart_limits", "structure_tags_general", "genre_smart_neighbors", "genre_random_rules", "quality_limits", "quality_presets"}:
                smart_rules_payload[key] = value
                continue
            if key == "ready_game_background_prompts" and isinstance(value, list):
                for entry in value:
                    if not isinstance(entry, dict):
                        continue
                    prompt = str(entry.get("prompt", "")).strip()
                    if not prompt:
                        continue
                    ready_prompts_payload.append(
                        {
                            "name": str(entry.get("name", "Untitled")).strip() or "Untitled",
                            "prompt": prompt,
                            "description": str(entry.get("ru", "")).strip(),
                        }
                    )
                continue

            if isinstance(value, list):
                token_payload[key] = value

        existing_prompt_data = self.storage.load_prompt_data()
        existing_user_prompts = self.storage.load_user_prompts()
        existing_smart_rules = self.storage.load_smart_rules()

        merged_prompt_data, added_categories, added_tokens = merge_prompt_data_with_stats(
            existing_prompt_data,
            token_payload,
        )
        merged_user_prompts, added_prompts = merge_user_prompts_with_stats(
            existing_user_prompts,
            ready_prompts_payload,
        )
        merged_smart_rules, added_rules = merge_smart_rules_with_stats(existing_smart_rules, smart_rules_payload)

        self.storage.save_prompt_data(merged_prompt_data)
        self.storage.save_user_prompts(merged_user_prompts)
        if smart_rules_payload:
            self.storage.save_smart_rules(merged_smart_rules)

        self.prompt_data = merged_prompt_data
        self.user_prompts = merged_user_prompts
        if smart_rules_payload:
            self.smart_rules = merged_smart_rules
        self.track_type_category = self._detect_track_type_category()
        self._rebuild_all_tokens_cache()

        self._reload_track_type_combo()
        self._render_cards()
        self.refresh_saved_prompts_table()
        self.update_prompt_preview()

        QMessageBox.information(
            self,
            "Import Pack",
            f"Импорт завершён. Добавлено: {added_categories} категорий, {added_tokens} токенов, {added_prompts} готовых промтов, {added_rules if smart_rules_payload else 0} smart rules.",
        )

    def set_language(self, lang: str) -> None:
        self.lang = lang
        self._persist_settings()
        self._apply_language()

    def _persist_settings(self) -> None:
        settings = self.storage.load_settings()
        settings["language"] = self.lang
        settings["display_mode"] = self.display_mode
        settings["theme"] = self.theme
        settings["generator_mode"] = self.generator_mode
        settings["auto_bgm_rules_enabled"] = self.auto_bgm_rules_enabled
        settings["structured_mode_enabled"] = self.structured_mode_enabled
        settings["favorites"] = sorted(self.favorites)
        settings["recent_token_ids"] = self.recent_token_ids[:200]
        settings.setdefault("ui", {})
        if isinstance(settings["ui"], dict):
            settings["ui"]["card_size"] = self.card_size
        settings.setdefault("ui_layout", {})
        if isinstance(settings["ui_layout"], dict):
            settings["ui_layout"]["main_vertical_splitter"] = self.main_vertical_splitter.sizes() if hasattr(self, "main_vertical_splitter") else [620, 240]
            settings["ui_layout"]["top_content_splitter"] = self.top_content_splitter.sizes() if hasattr(self, "top_content_splitter") else [260, 840]
            settings["ui_layout"]["prompt_area_splitter"] = self.prompt_area_splitter.sizes() if hasattr(self, "prompt_area_splitter") else [700, 300]
            settings["ui_layout"]["bottom_prompt_splitter"] = self.bottom_prompt_splitter.sizes() if hasattr(self, "bottom_prompt_splitter") else [780, 420]
            settings["ui_layout"]["sidebar_collapsed"] = not self.sidebar_toggle_btn.isChecked() if hasattr(self, "sidebar_toggle_btn") else False
            settings["ui_layout"]["prompt_collapsed"] = not self.prompt_toggle_btn.isChecked() if hasattr(self, "prompt_toggle_btn") else False
            settings["ui_layout"]["smart_collapsed"] = not self.smart_toggle_btn.isChecked() if hasattr(self, "smart_toggle_btn") else False
            settings["ui_layout"]["warnings_collapsed"] = not self.warnings_toggle_btn.isChecked() if hasattr(self, "warnings_toggle_btn") else False
            settings["ui_layout"]["saved_collapsed"] = not self.saved_toggle_btn.isChecked() if hasattr(self, "saved_toggle_btn") else False
        self.storage.save_settings(settings)

    def _detect_track_type_category(self) -> str:
        aliases = {"тип трека", "track type", "track_type", "tracktype"}
        for key in self.prompt_data.keys():
            normalized = key.strip().lower().replace("_", " ")
            if normalized in aliases:
                return key
        return next(iter(self.prompt_data.keys()))

    def _on_preset_selected(self, index: int) -> None:
        if index <= 0:
            return
        name = self.preset_combo.currentText()
        self.apply_preset_tags(self.presets.get(name, []))

    def apply_preset_tags(self, tags: List[str]) -> None:
        self.clear_selection()
        self.active_collection_name = None
        self.active_structure_tags = []
        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}
        track_types = {token.get("en", "") for token in self.prompt_data.get(self.track_type_category, []) if isinstance(token, dict)}
        for tag in tags:
            if tag in track_types:
                self.track_type_combo.setCurrentText(tag)
                break

        for token in self._all_tokens():
            if token["en"] in tags:
                self.selected_tokens[token["id"]] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": 1.0,
                }

        self._render_cards()
        self.update_prompt_preview()

    def save_preset(self) -> None:
        name, accepted = QInputDialog.getText(self, "Preset", "Preset name:")
        if not accepted:
            return
        name = name.strip()
        if not name:
            return

        tags = [self.track_type_combo.currentText()] + [item["en"] for item in self.selected_tokens.values()]
        overwrite = True
        existing = self.storage.load_presets()
        if name in existing:
            answer = QMessageBox.question(
                self,
                "Preset exists",
                "Перезаписать пресет?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            overwrite = answer == QMessageBox.StandardButton.Yes

        saved_name = self.storage.save_preset(name, tags, overwrite=overwrite)
        self.presets = self.storage.load_presets()
        self._reload_presets_combo()
        self.preset_combo.setCurrentText(saved_name)

    def clear_selection(self) -> None:
        self.selected_tokens = {}
        self.active_collection_name = None
        self.active_structure_tags = []
        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}
        self.track_type_combo.setCurrentText("instrumental") if self.track_type_combo.findText("instrumental") >= 0 else None
        self._render_cards()
        self.update_prompt_preview()

    def apply_random_selection(self) -> None:
        self.clear_selection()
        self._apply_genre_random_selection()
        buckets = {
            "vocals": (0, 2),
            "mood": (2, 4),
            "texture": (1, 3),
            "ambient": (1, 3),
        }
        all_tokens = self._all_tokens()

        instrument_groups = [category for category in self._instrument_group_categories() if any(token.get("category") == category for token in all_tokens)]
        random.shuffle(instrument_groups)
        for category in instrument_groups[:4]:
            candidates = [token for token in all_tokens if token.get("category") == category]
            if not candidates:
                continue
            sample_count = min(1, len(candidates))
            for token in random.sample(candidates, sample_count):
                self.selected_tokens[token["id"]] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": 1.0,
                }

        for tab, (min_count, max_count) in buckets.items():
            candidates = [token for token in all_tokens if self._token_in_tab(token, tab)]
            if not candidates:
                continue
            count = random.randint(min_count, min(max_count, len(candidates)))
            for token in random.sample(candidates, count):
                self.selected_tokens[token["id"]] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": 1.0,
                }
        self.active_structure_tags = []
        self._render_cards()
        self.update_prompt_preview()

    def _apply_genre_random_selection(self) -> None:
        all_tokens = [token for token in self._all_tokens() if str(token.get("category", "")).lower().startswith("genre_")]
        if not all_tokens:
            return

        grouped: Dict[str, List[Dict[str, str]]] = {}
        for token in all_tokens:
            grouped.setdefault(token["category"], []).append(token)

        rules = self.smart_rules.get("genre_random_rules", {}) if isinstance(self.smart_rules, dict) else {}
        if not isinstance(rules, dict):
            rules = {}

        max_total = int(rules.get("max_total", 3))
        sub_min = int(rules.get("sub_min", 1))
        sub_max = int(rules.get("sub_max", 2))
        hybrid_chance = float(rules.get("hybrid_chance", 0.35))
        hybrid_candidates = [str(cat) for cat in rules.get("hybrid_candidates", []) if isinstance(cat, str) and cat in grouped]

        main_group = random.choice(list(grouped.keys()))
        picked_ids: set[str] = set()

        def pick_from_group(category: str) -> None:
            options = [token for token in grouped.get(category, []) if token["id"] not in picked_ids]
            if not options:
                return
            token = random.choice(options)
            picked_ids.add(token["id"])
            self.selected_tokens[token["id"]] = {
                "category": token["category"],
                "en": token["en"],
                "weight": 1.0,
            }

        pick_from_group(main_group)

        other_groups = [group for group in grouped.keys() if group != main_group]
        random.shuffle(other_groups)
        sub_count = random.randint(max(0, sub_min), max(0, min(sub_max, len(other_groups))))
        for category in other_groups[:sub_count]:
            if len(picked_ids) >= max_total:
                break
            pick_from_group(category)

        if len(picked_ids) < max_total and random.random() <= hybrid_chance:
            pool = [cat for cat in hybrid_candidates if cat != main_group] or other_groups
            random.shuffle(pool)
            for category in pool:
                if len(picked_ids) >= max_total:
                    break
                pick_from_group(category)

    def apply_collection(self) -> None:
        name = self.collection_combo.currentText()
        values = COLLECTIONS.get(name, [])
        if not values:
            return
        self.active_collection_name = name
        self.active_structure_tags = []
        self.last_smart_action = {"added_tokens": [], "structure_tags": [], "mode": "", "timestamp": ""}
        value_set = {value.lower() for value in values}
        for token in self._all_tokens():
            if token["en"].lower() in value_set:
                self.selected_tokens[token["id"]] = {
                    "category": token["category"],
                    "en": token["en"],
                    "weight": 1.0,
                }
        self._render_cards()
        self.update_prompt_preview()

    def save_current_prompt(self) -> None:
        prompt_text = self.full_prompt_edit.toPlainText().strip()
        if not prompt_text:
            return
        name, accepted = QInputDialog.getText(self, "Prompt", "Prompt name:")
        if not accepted:
            return
        self.storage.add_user_prompt(name.strip() or "Untitled", prompt_text)
        self.refresh_saved_prompts_table()

    def add_ready_prompt(self) -> None:
        dialog = AddPromptDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        payload = dialog.data()
        if not payload["prompt"]:
            QMessageBox.warning(self, "Error", "Prompt is empty")
            return
        self.storage.add_user_prompt(payload["name"] or "Untitled", payload["prompt"], payload["description"])
        self.refresh_saved_prompts_table()

    def add_token(self) -> None:
        dialog = AddTokenDialog(list(self.prompt_data.keys()), self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        payload = dialog.data()
        category = payload["category"]
        en_value = payload["en"]
        ru_value = payload["ru"]

        if not category or not en_value:
            return

        if category not in self.prompt_data:
            self.prompt_data[category] = []

        existing = {
            str(item.get("en", "")).strip().lower()
            for item in self.prompt_data.get(category, [])
            if isinstance(item, dict)
        }
        if en_value.strip().lower() in existing:
            QMessageBox.information(self, "Info", "Такой токен уже есть")
            return

        token: Dict[str, str] = {"en": en_value.strip()}
        if ru_value.strip():
            token["ru"] = ru_value.strip()

        self.prompt_data[category].append(token)
        self.storage.save_prompt_data(self.prompt_data)

        self.prompt_data = self.storage.load_prompt_data()
        self.track_type_category = self._detect_track_type_category()
        self._rebuild_all_tokens_cache()
        self._reload_track_type_combo()
        self._render_cards()

    def import_json(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(self, "Import JSON", str(self.storage.base_dir), "JSON Files (*.json)")
        if not file_name:
            return

        try:
            raw = load_json_file(Path(file_name))
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "JSON повреждён. Импорт отменён.")
            return
        except Exception as exc:  # pragma: no cover
            QMessageBox.critical(self, "Error", f"Read error: {exc}")
            return

        detected_type, payload = detect_import_payload(raw)
        if detected_type == "invalid":
            QMessageBox.warning(self, "Error", "Файл JSON распознан, но структура не подходит для импорта.")
            return

        existing_prompt_data = self.storage.load_prompt_data()
        existing_presets = self.storage.load_presets()
        existing_user_prompts = self.storage.load_user_prompts()
        existing_smart_rules = self.storage.load_smart_rules()

        merged_prompt_data, added_categories, added_tokens = merge_prompt_data_with_stats(
            existing_prompt_data, payload.get("prompt_data", {})
        )
        merged_presets, added_presets = merge_presets_with_stats(existing_presets, payload.get("presets", {}))
        merged_user_prompts, added_prompts = merge_user_prompts_with_stats(
            existing_user_prompts, payload.get("user_prompts", [])
        )
        merged_smart_rules, added_rules = merge_smart_rules_with_stats(existing_smart_rules, payload.get("smart_rules", {}))

        self.storage.save_prompt_data(merged_prompt_data)
        self.storage.save_presets(merged_presets)
        self.storage.save_user_prompts(merged_user_prompts)
        self.storage.save_smart_rules(merged_smart_rules)

        self.prompt_data = merged_prompt_data
        self.presets = merged_presets
        self.user_prompts = merged_user_prompts
        self.smart_rules = merged_smart_rules
        self.track_type_category = self._detect_track_type_category()
        self._rebuild_all_tokens_cache()

        self._reload_track_type_combo()
        self._reload_presets_combo()
        self._render_cards()
        self.refresh_saved_prompts_table()
        self.update_prompt_preview()

        QMessageBox.information(
            self,
            "Import",
            (
                "Импорт завершён. "
                f"Добавлено: {added_categories} категорий, {added_tokens} токенов, "
                f"{added_presets} пресетов, {added_prompts} промтов, {added_rules} smart rules."
            ),
        )

    def _export_payload(self, payload: Any, default_name: str) -> None:
        self.storage.ensure_data_files()
        default_path = str(self.storage.exports_dir / default_name)
        file_name, _ = QFileDialog.getSaveFileName(self, "Export JSON", default_path, "JSON Files (*.json)")
        if not file_name:
            return
        save_json_file(Path(file_name), payload)
        self.statusBar().showMessage("Export done", 1500)

    def export_all_data(self) -> None:
        payload = build_combined_export(
            self.storage.load_prompt_data(),
            self.storage.load_presets(),
            self.storage.load_user_prompts(),
            self.storage.load_smart_rules(),
        )
        self._export_payload(payload, default_export_filename("suno_prompt_export"))

    def export_prompt_data(self) -> None:
        self._export_payload(self.storage.load_prompt_data(), default_export_filename("suno_prompt_tokens"))

    def export_presets(self) -> None:
        self._export_payload(self.storage.load_presets(), default_export_filename("suno_prompt_presets"))

    def export_user_prompts(self) -> None:
        self._export_payload(self.storage.load_user_prompts(), default_export_filename("suno_prompt_prompts"))

    def refresh_saved_prompts_table(self) -> None:
        self.user_prompts = self.storage.load_user_prompts()
        self.saved_table.setRowCount(len(self.user_prompts))

        for row, item in enumerate(self.user_prompts):
            self.saved_table.setItem(row, 0, QTableWidgetItem(item.get("name", "Untitled")))
            self.saved_table.setItem(row, 1, QTableWidgetItem(item.get("created_at", "")))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)

            load_btn = QPushButton(t(self.lang, "load"))
            load_btn.setProperty("row", row)
            load_btn.clicked.connect(self.load_saved_prompt)

            copy_btn = QPushButton(t(self.lang, "copy"))
            copy_btn.setProperty("row", row)
            copy_btn.clicked.connect(self.copy_saved_prompt)

            delete_btn = QPushButton(t(self.lang, "delete"))
            delete_btn.setProperty("row", row)
            delete_btn.clicked.connect(self.delete_saved_prompt)

            actions_layout.addWidget(load_btn)
            actions_layout.addWidget(copy_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()

            self.saved_table.setCellWidget(row, 2, actions_widget)

    def _sender_row(self) -> int:
        sender = self.sender()
        if sender is None:
            return -1
        return int(sender.property("row"))

    def load_saved_prompt(self) -> None:
        row = self._sender_row()
        if row < 0 or row >= len(self.user_prompts):
            return
        prompt_text = self.user_prompts[row].get("prompt", "")
        self.full_prompt_edit.setPlainText(prompt_text)
        short_parts = [part.strip() for part in prompt_text.split(",") if part.strip()]
        self.short_prompt_edit.setPlainText(build_short_prompt(short_parts, 120))

    def copy_saved_prompt(self) -> None:
        row = self._sender_row()
        if row < 0 or row >= len(self.user_prompts):
            return
        self._copy_text(self.user_prompts[row].get("prompt", ""))

    def delete_saved_prompt(self) -> None:
        row = self._sender_row()
        if row < 0 or row >= len(self.user_prompts):
            return
        self.storage.delete_user_prompt_at(row)
        self.refresh_saved_prompts_table()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self._persist_settings()
        super().closeEvent(event)
