from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_PROMPT_DATA: Dict[str, List[Dict[str, str]]] = {
    "Тип трека": [
        {"en": "instrumental", "ru": "инструментал"},
        {"en": "vocal track", "ru": "вокальный трек"},
        {"en": "beat", "ru": "бит"},
        {"en": "background music", "ru": "фоновая музыка"},
        {"en": "cinematic soundtrack", "ru": "кинематографичный саундтрек"},
    ],
    "Жанр": [
        {"en": "dark boom bap", "ru": "мрачный boom bap"},
        {"en": "underground hip-hop", "ru": "андеграунд хип-хоп"},
        {"en": "classic boom bap", "ru": "классический boom bap"},
        {"en": "trap", "ru": "трэп"},
        {"en": "dark trap", "ru": "мрачный трэп"},
        {"en": "phonk", "ru": "фонк"},
        {"en": "lo-fi hip-hop", "ru": "лоуфай хип-хоп"},
        {"en": "ambient", "ru": "эмбиент"},
        {"en": "dark ambient", "ru": "мрачный эмбиент"},
        {"en": "EDM", "ru": "EDM"},
        {"en": "house", "ru": "хаус"},
        {"en": "techno", "ru": "техно"},
        {"en": "drum and bass", "ru": "драм-н-бейс"},
        {"en": "jazz noir", "ru": "джаз-нуар"},
        {"en": "1960s cartoon noir soundtrack", "ru": "саундтрек нуарного мультфильма 1960-х"},
        {"en": "cinematic horror", "ru": "кинематографичный хоррор"},
        {"en": "dark fantasy soundtrack", "ru": "саундтрек тёмного фэнтези"},
        {"en": "slavic folk fusion", "ru": "славянский фолк-фьюжн"},
        {"en": "middle eastern fusion", "ru": "ближневосточный фьюжн"},
        {"en": "japanese traditional fusion", "ru": "японский традиционный фьюжн"},
    ],
    "Инструменты": [
        {"en": "slow melancholic piano", "ru": "медленное меланхоличное пианино"},
        {"en": "detuned piano", "ru": "расстроенное пианино"},
        {"en": "dark strings", "ru": "мрачные струнные"},
        {"en": "sharp violin stabs", "ru": "резкие скрипичные уколы"},
        {"en": "deep dark cello", "ru": "глубокая мрачная виолончель"},
        {"en": "tremolo violins", "ru": "тремоло скрипок"},
        {"en": "screeching violins", "ru": "визжащие скрипки"},
        {"en": "muted trumpet", "ru": "сурдиновая труба"},
        {"en": "soft saxophone", "ru": "мягкий саксофон"},
        {"en": "upright bass", "ru": "контрабас"},
        {"en": "vibraphone", "ru": "вибрафон"},
        {"en": "brush drums", "ru": "барабаны щётками"},
        {"en": "dusty boom bap drums", "ru": "пыльные boom bap барабаны"},
        {"en": "808 bass", "ru": "808 бас"},
        {"en": "tribal drums", "ru": "племенные барабаны"},
        {"en": "shamanic frame drum", "ru": "шаманский бубен"},
        {"en": "vinyl scratches", "ru": "виниловые скретчи"},
        {"en": "DJ Premier style scratches", "ru": "скретчи в стиле DJ Premier"},
        {"en": "raw turntable cuts", "ru": "сырые порезки вертушки"},
    ],
    "Вокал / напевы": [
        {"en": "no vocals", "ru": "без вокала"},
        {"en": "soft fragile male vocals", "ru": "мягкий хрупкий мужской вокал"},
        {"en": "breathy female vocals", "ru": "дыхательный женский вокал"},
        {"en": "whispered phrases", "ru": "шёпотные фразы"},
        {"en": "broken emotional vocals", "ru": "ломаный эмоциональный вокал"},
        {"en": "distant ghostly vocals", "ru": "далёкий призрачный вокал"},
        {"en": "ritual chanting", "ru": "ритуальные песнопения"},
        {"en": "ancient Slavic chanting", "ru": "древнеславянские песнопения"},
        {"en": "shamanic chanting", "ru": "шаманские песнопения"},
        {"en": "Arabic melismatic singing", "ru": "арабский мелизматический вокал"},
        {"en": "Japanese monk chanting", "ru": "песнопения японских монахов"},
        {"en": "wordless humming", "ru": "безсловесное гудение"},
        {"en": "soft murmuring", "ru": "мягкое бормотание"},
        {"en": "wailing voices", "ru": "причитающие голоса"},
        {"en": "call and response vocals", "ru": "вокал вопрос-ответ"},
        {"en": "unknown ancient language", "ru": "неизвестный древний язык"},
    ],
    "Настроение": [
        {"en": "dark", "ru": "мрачное"},
        {"en": "melancholic", "ru": "меланхоличное"},
        {"en": "lonely", "ru": "одинокое"},
        {"en": "hopeless", "ru": "безнадёжное"},
        {"en": "nostalgic", "ru": "ностальгичное"},
        {"en": "sinister", "ru": "зловещее"},
        {"en": "eerie", "ru": "жуткое"},
        {"en": "haunting", "ru": "преследующее"},
        {"en": "cold and distant", "ru": "холодное и далёкое"},
        {"en": "ritualistic", "ru": "ритуалистичное"},
        {"en": "tragic", "ru": "трагичное"},
        {"en": "psychological tension", "ru": "психологическое напряжение"},
        {"en": "quiet despair", "ru": "тихое отчаяние"},
        {"en": "dark nostalgia", "ru": "тёмная ностальгия"},
    ],
    "Текстура": [
        {"en": "lo-fi texture", "ru": "лоуфай текстура"},
        {"en": "vinyl crackle", "ru": "виниловый треск"},
        {"en": "tape hiss", "ru": "ленточное шипение"},
        {"en": "analog warmth", "ru": "аналоговое тепло"},
        {"en": "warped tape sound", "ru": "деформированный лентный звук"},
        {"en": "dusty sound", "ru": "пыльный звук"},
        {"en": "long reverb", "ru": "длинный реверб"},
        {"en": "distant echo", "ru": "далёкое эхо"},
        {"en": "empty space", "ru": "пустое пространство"},
        {"en": "old film texture", "ru": "текстура старой плёнки"},
        {"en": "degraded vintage audio", "ru": "деградированный винтажный звук"},
    ],
    "Характер": [
        {"en": "minimalistic arrangement", "ru": "минималистичная аранжировка"},
        {"en": "slow tempo", "ru": "медленный темп"},
        {"en": "broken rhythm", "ru": "ломаный ритм"},
        {"en": "unresolved chords", "ru": "неразрешённые аккорды"},
        {"en": "dissonant harmonies", "ru": "диссонантные гармонии"},
        {"en": "sudden stabs", "ru": "внезапные уколы"},
        {"en": "hypnotic repetition", "ru": "гипнотическая повторяемость"},
        {"en": "gradual build-up", "ru": "постепенное нарастание"},
        {"en": "cinematic structure", "ru": "кинематографичная структура"},
        {"en": "vintage cartoon vibe", "ru": "вайб винтажного мультфильма"},
        {"en": "raw underground sound", "ru": "сырой андеграундный звук"},
    ],
    "Дополнительно": [
        {"en": "clean mix", "ru": "чистый микс"},
        {"en": "wide stereo image", "ru": "широкая стереобаза"},
        {"en": "high dynamic range", "ru": "высокий динамический диапазон"},
    ],
}

DEFAULT_PRESETS: Dict[str, List[str]] = {
    "Мрачный мульт 60-х": [
        "instrumental",
        "1960s cartoon noir soundtrack",
        "jazz noir",
        "detuned piano",
        "muted trumpet",
        "upright bass",
        "vibraphone",
        "brush drums",
        "dark",
        "eerie",
        "melancholic",
        "old film texture",
        "vinyl crackle",
        "analog warmth",
        "vintage cartoon vibe",
        "slow tempo",
    ],
    "Тёмный boom bap": [
        "beat",
        "dark boom bap",
        "underground hip-hop",
        "dusty boom bap drums",
        "808 bass",
        "vinyl scratches",
        "DJ Premier style scratches",
        "dark",
        "nostalgic",
        "raw underground sound",
        "lo-fi texture",
        "vinyl crackle",
    ],
    "Ритуальный хоррор": [
        "cinematic soundtrack",
        "cinematic horror",
        "dark ambient",
        "tribal drums",
        "shamanic frame drum",
        "deep dark cello",
        "ritual chanting",
        "unknown ancient language",
        "dark",
        "ritualistic",
        "psychological tension",
        "long reverb",
        "distant echo",
        "cinematic structure",
    ],
    "Печальное пианино": [
        "instrumental",
        "ambient",
        "slow melancholic piano",
        "detuned piano",
        "no vocals",
        "melancholic",
        "lonely",
        "quiet despair",
        "analog warmth",
        "empty space",
        "minimalistic arrangement",
        "slow tempo",
    ],
    "Славянский тёмный напев": [
        "vocal track",
        "slavic folk fusion",
        "dark fantasy soundtrack",
        "dark strings",
        "ancient Slavic chanting",
        "wordless humming",
        "dark",
        "haunting",
        "tragic",
        "old film texture",
        "long reverb",
        "hypnotic repetition",
    ],
    "Арабская пустынная тоска": [
        "vocal track",
        "middle eastern fusion",
        "ambient",
        "soft saxophone",
        "tribal drums",
        "Arabic melismatic singing",
        "nostalgic",
        "lonely",
        "dark nostalgia",
        "distant echo",
        "dusty sound",
        "gradual build-up",
    ],
    "Японский ритуальный ambient": [
        "background music",
        "japanese traditional fusion",
        "dark ambient",
        "tremolo violins",
        "Japanese monk chanting",
        "soft murmuring",
        "eerie",
        "cold and distant",
        "ritualistic",
        "tape hiss",
        "empty space",
        "minimalistic arrangement",
        "hypnotic repetition",
    ],
}

INSTRUMENT_GROUPS_PACK_FILENAME = "instrument_groups_pack.json"
MEGA_GENRE_PACK_FILENAME = "mega_genre_pack.json"
QUALITY_MIX_MASTERING_PACK_FILENAME = "quality_mix_mastering_pack.json"


class Storage:
    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.data_dir = self.base_dir / "data"
        self.exports_dir = self.base_dir / "exports"
        self.prompt_data_path = self.data_dir / "prompt_data.json"
        self.instrument_groups_pack_path = self.data_dir / INSTRUMENT_GROUPS_PACK_FILENAME
        self.mega_genre_pack_path = self.data_dir / MEGA_GENRE_PACK_FILENAME
        self.quality_mix_mastering_pack_path = self.data_dir / QUALITY_MIX_MASTERING_PACK_FILENAME
        self.presets_path = self.data_dir / "presets.json"
        self.user_prompts_path = self.data_dir / "user_prompts.json"
        self.settings_path = self.data_dir / "user_settings.json"
        self.smart_rules_path = self.data_dir / "smart_rules.json"

    def ensure_data_files(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_file(self.prompt_data_path, DEFAULT_PROMPT_DATA)
        self._ensure_file(self.presets_path, DEFAULT_PRESETS)
        self._ensure_file(self.user_prompts_path, [])
        self._ensure_file(
            self.smart_rules_path,
            {
                "global_rules": {},
                "mode_rules": {},
                "genre_rules": {},
                "mood_rules": {},
                "instrument_rules": {},
                "vocal_rules": {},
                "texture_rules": {},
                "performance_rules": {},
                "collection_rules": {},
                "conflict_rules": [],
                "smart_limits": {
                    "max_total_added": 14,
                    "max_genres": 2,
                    "max_instruments": 5,
                    "max_vocals": 3,
                    "max_moods": 4,
                    "max_textures": 4,
                    "max_performance": 4,
                    "max_negative": 4,
                    "max_structure_tags": 3,
                },
                "quality_limits": {
                    "max_quality_tokens_total": 6,
                    "max_quality_tokens_per_group": 2,
                    "warn_if_more_than": 6,
                },
                "quality_presets": [
                    {
                        "name": "Clean Studio",
                        "ru": "Чистая студия",
                        "tokens": [
                            "studio quality",
                            "clean mix",
                            "balanced EQ",
                            "wide stereo",
                            "clean master",
                            "no muddy mix",
                        ],
                    },
                    {
                        "name": "Warm Analog",
                        "ru": "Тёплый аналог",
                        "tokens": [
                            "analog warmth",
                            "tape saturation",
                            "warm low end",
                            "soft compression",
                            "smooth high end",
                        ],
                    },
                    {
                        "name": "Lo-Fi Tape",
                        "ru": "Lo-Fi плёнка",
                        "tokens": ["lo-fi texture", "tape hiss", "vinyl crackle", "warped tape", "dusty old recording"],
                    },
                    {
                        "name": "Modern Trap Mix",
                        "ru": "Современный trap-микс",
                        "tokens": ["modern trap mix", "deep 808 bass", "tight low end", "crisp hi-hats", "loud but clean master"],
                    },
                    {
                        "name": "Cinematic Wide",
                        "ru": "Широкое кино",
                        "tokens": ["cinematic mix", "wide stereo image", "deep cinematic reverb", "orchestral hall sound", "wide dynamic range"],
                    },
                    {
                        "name": "Vocal Forward",
                        "ru": "Вокал вперёд",
                        "tokens": ["clear vocals", "vocal forward mix", "centered lead vocal", "smooth vocal compression", "no buried vocals"],
                    },
                    {
                        "name": "Dusty Boom Bap",
                        "ru": "Пыльный boom bap",
                        "tokens": ["dusty drums", "vinyl crackle", "dirty analog texture", "warm low end", "sample-based texture"],
                    },
                ],
                "structure_tags_general": [],
            },
        )
        self._ensure_file(
            self.settings_path,
            {
                "language": "ru",
                "display_mode": "both",
                "theme": "dark_noir",
                "favorites": [],
                "recent_token_ids": [],
                "ui": {
                    "card_size": "medium",
                },
                "ui_layout": {
                    "main_vertical_splitter": [620, 240],
                    "top_content_splitter": [260, 840],
                    "prompt_area_splitter": [160, 120],
                    "bottom_prompt_splitter": [780, 420],
                    "sidebar_collapsed": False,
                    "prompt_collapsed": False,
                    "smart_collapsed": False,
                    "warnings_collapsed": False,
                    "saved_collapsed": False,
                },
            },
        )
        self._merge_pack_into_prompt_data(self.instrument_groups_pack_path)
        self._merge_pack_into_prompt_data(self.mega_genre_pack_path)
        self._merge_pack_into_prompt_data(self.quality_mix_mastering_pack_path)

    def _merge_pack_into_prompt_data(self, pack_path: Path) -> None:
        if not pack_path.exists():
            return
        try:
            with pack_path.open("r", encoding="utf-8") as f:
                pack = json.load(f)
        except (json.JSONDecodeError, OSError):
            return

        if not isinstance(pack, dict):
            return

        try:
            with self.prompt_data_path.open("r", encoding="utf-8") as f:
                prompt_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            prompt_data = {}

        if not isinstance(prompt_data, dict):
            prompt_data = {}

        changed = False
        for category, items in pack.items():
            if not isinstance(category, str) or not isinstance(items, list):
                continue

            existing_items = prompt_data.setdefault(category, [])
            if not isinstance(existing_items, list):
                prompt_data[category] = []
                existing_items = prompt_data[category]

            seen_en = {
                str(item.get("en", "")).strip().lower()
                for item in existing_items
                if isinstance(item, dict) and str(item.get("en", "")).strip()
            }

            for item in items:
                if not isinstance(item, dict):
                    continue
                en_value = str(item.get("en", "")).strip()
                if not en_value:
                    continue
                key = en_value.lower()
                if key in seen_en:
                    continue
                token: Dict[str, str] = {"en": en_value, "ru": str(item.get("ru", "")).strip()}
                existing_items.append(token)
                seen_en.add(key)
                changed = True

        if changed:
            with self.prompt_data_path.open("w", encoding="utf-8") as f:
                json.dump(prompt_data, f, ensure_ascii=False, indent=2)

    def load_prompt_data(self) -> Dict[str, Any]:
        self.ensure_data_files()
        with self.prompt_data_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_presets(self) -> Dict[str, List[str]]:
        self.ensure_data_files()
        with self.presets_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {str(name): [str(tag) for tag in tags] for name, tags in data.items()}

    def save_preset(self, name: str, tags: List[str], overwrite: bool = True) -> str:
        presets = self.load_presets()
        unique_tags = list(dict.fromkeys([tag.strip() for tag in tags if tag and tag.strip()]))
        target_name = name if overwrite or name not in presets else self.make_unique_preset_name(name, presets)
        presets[target_name] = unique_tags
        self.save_presets(presets)
        return target_name

    def make_unique_preset_name(self, base_name: str, presets: Dict[str, List[str]] | None = None) -> str:
        all_presets = presets if presets is not None else self.load_presets()
        if base_name not in all_presets:
            return base_name
        index = 2
        while f"{base_name} ({index})" in all_presets:
            index += 1
        return f"{base_name} ({index})"

    def save_presets(self, presets: Dict[str, List[str]]) -> None:
        self.ensure_data_files()
        with self.presets_path.open("w", encoding="utf-8") as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)

    def save_prompt_data(self, prompt_data: Dict[str, Any]) -> None:
        self.ensure_data_files()
        with self.prompt_data_path.open("w", encoding="utf-8") as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=2)

    def load_user_prompts(self) -> List[Dict[str, str]]:
        self.ensure_data_files()
        with self.user_prompts_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        normalized: List[Dict[str, str]] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            prompt = str(item.get("prompt", "")).strip()
            if not prompt:
                continue
            normalized.append(
                {
                    "name": str(item.get("name", "Untitled")).strip() or "Untitled",
                    "prompt": prompt,
                    "created_at": str(item.get("created_at", "")).strip() or self.now_string(),
                    "description": str(item.get("description", "")).strip(),
                }
            )
        return normalized

    def save_user_prompts(self, prompts: List[Dict[str, str]]) -> None:
        self.ensure_data_files()
        with self.user_prompts_path.open("w", encoding="utf-8") as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)

    def add_user_prompt(self, name: str, prompt: str, description: str = "") -> None:
        prompts = self.load_user_prompts()
        prompts.append(
            {
                "name": name.strip() or "Untitled",
                "prompt": prompt.strip(),
                "created_at": self.now_string(),
                "description": description.strip(),
            }
        )
        self.save_user_prompts(prompts)

    def delete_user_prompt_at(self, index: int) -> None:
        prompts = self.load_user_prompts()
        if 0 <= index < len(prompts):
            prompts.pop(index)
            self.save_user_prompts(prompts)

    def load_settings(self) -> Dict[str, Any]:
        self.ensure_data_files()
        with self.settings_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        return data

    def load_smart_rules(self) -> Dict[str, Any]:
        self.ensure_data_files()
        try:
            with self.smart_rules_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            data = {}

        if not isinstance(data, dict):
            return {
                "global_rules": {},
                "mode_rules": {},
                "genre_rules": {},
                "mood_rules": {},
                "instrument_rules": {},
                "vocal_rules": {},
                "texture_rules": {},
                "performance_rules": {},
                "collection_rules": {},
                "conflict_rules": [],
                "smart_limits": {},
                "quality_limits": {},
                "quality_presets": [],
                "structure_tags_general": [],
            }
        return data

    def save_smart_rules(self, smart_rules: Dict[str, Any]) -> None:
        self.ensure_data_files()
        with self.smart_rules_path.open("w", encoding="utf-8") as f:
            json.dump(smart_rules, f, ensure_ascii=False, indent=2)

    def save_settings(self, settings: Dict[str, Any]) -> None:
        self.ensure_data_files()
        with self.settings_path.open("w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    def load_favorites(self) -> List[str]:
        settings = self.load_settings()
        raw = settings.get("favorites", [])
        if not isinstance(raw, list):
            return []
        return [str(item) for item in raw if str(item).strip()]

    def save_favorites(self, favorites: List[str]) -> None:
        settings = self.load_settings()
        settings["favorites"] = list(dict.fromkeys([item for item in favorites if item]))
        self.save_settings(settings)

    @staticmethod
    def now_string() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _ensure_file(path: Path, default_data: Any) -> None:
        if path.exists():
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
