from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple


DEFAULT_SMART_LIMITS = {
    "max_total_added": 14,
    "max_genres": 2,
    "max_instruments": 5,
    "max_instruments_total": 6,
    "max_instruments_per_group": 2,
    "max_rare_instruments": 2,
    "max_sound_design_fx": 3,
    "max_vocals": 3,
    "max_moods": 4,
    "max_textures": 4,
    "max_performance": 4,
    "max_negative": 4,
    "max_structure_tags": 3,
    "max_quality_tokens_total": 6,
}

DEFAULT_STRUCTURE_TAGS = [
    {"en": "[Intro]", "ru": "вступление"},
    {"en": "[Verse]", "ru": "куплет"},
    {"en": "[Chorus]", "ru": "припев"},
    {"en": "[Bridge]", "ru": "бридж"},
    {"en": "[Outro]", "ru": "аутро"},
    {"en": "[Instrumental]", "ru": "инструментал"},
    {"en": "[Instrumental Break]", "ru": "инструментальная пауза"},
    {"en": "[Beat Drop]", "ru": "дроп"},
    {"en": "[Build Up]", "ru": "нарастание"},
    {"en": "[Scratch Break]", "ru": "скрэтч-пауза"},
    {"en": "[Piano Intro]", "ru": "пианино-интро"},
    {"en": "[String Section]", "ru": "струнная секция"},
    {"en": "[Choir Enters]", "ru": "входит хор"},
    {"en": "[Ambient Interlude]", "ru": "эмбиентная интерлюдия"},
    {"en": "[Fade Out]", "ru": "затухание"},
]

CATEGORY_BUCKETS = {
    "genres": "genres",
    "genre": "genres",
    "styles": "genres",
    "instruments": "instruments",
    "instrument": "instruments",
    "vocals": "vocals",
    "vocal": "vocals",
    "choir": "vocals",
    "chant": "vocals",
    "mood": "moods",
    "moods": "moods",
    "texture": "textures",
    "textures": "textures",
    "production": "textures",
    "performance": "performance",
    "technique": "performance",
    "negative": "negative",
    "negatives": "negative",
    "structure": "structure",
    "structure tags": "structure",
    "background": "performance",
    "bgm": "performance",
    "quality": "quality",
    "master": "quality",
    "mix": "quality",
    "eq": "quality",
    "stereo": "quality",
    "reverb": "quality",
}

RULE_SECTION_ORDER = (
    "global_rules",
    "mode_rules",
    "genre_rules",
    "mood_rules",
    "instrument_rules",
    "vocal_rules",
    "texture_rules",
    "performance_rules",
    "collection_rules",
    "genre_smart_neighbors",
)

MODE_RULE_ALIASES = {
    "smart_bgm": {"smart_bgm", "background", "background music", "game background", "game_background"},
    "background": {"background", "background music", "game background", "game_background"},
    "game_background": {"background", "background music", "game background", "game_background"},
}

CONTEXT_DEFINITIONS = [
    ("boom bap", ["boom bap", "hip-hop", "hip hop", "scratches", "turntable", "vinyl crackle"]),
    ("trap", ["trap", "808", "hi-hat", "hihat", "snare roll"]),
    ("ambient", ["ambient", "drone", "evolving layers", "atmosphere"]),
    ("dark ambient", ["dark ambient", "deep drone", "low frequency rumble"]),
    ("fantasy ambient", ["fantasy ambient", "ethereal choir", "wooden flute", "harp"]),
    ("cinematic horror", ["cinematic horror", "dissonant strings", "waterphone", "psychological tension"]),
    ("cartoon noir", ["cartoon noir", "jazz noir", "muted trumpet", "vibraphone"]),
    ("edm", ["edm", "house", "techno", "drum and bass", "sidechain"]),
    ("ritual", ["ritual", "chanting", "shamanic", "frame drum", "ancient"]),
    ("slavic", ["slavic", "gusli", "tagelharpa", "folk"]),
    ("middle eastern", ["middle eastern", "oud", "ney", "duduk", "arabic"]),
    ("japanese", ["japanese", "shakuhachi", "koto", "temple bells", "monk chanting"]),
    ("piano", ["piano", "detuned piano", "melancholic piano"]),
    ("strings", ["strings", "violin", "cello", "viola"]),
    ("choir", ["choir", "chant", "humming", "voices", "vocals"]),
    ("instrumental", ["instrumental", "no vocals", "no lyrics"]),
    ("beat", ["beat", "groove", "loopable beat structure"]),
    ("background music", ["background music", "loopable", "non-intrusive background music"]),
]

STRUCTURE_TRIGGER_MAP = [
    (["scratches", "turntable", "hip-hop", "boom bap", "vinyl crackle"], ["[Scratch Break]"]),
    (["edm", "house", "techno", "drum and bass", "drop", "build-up"], ["[Build Up]", "[Beat Drop]"]),
    (["piano", "detuned piano", "melancholic piano"], ["[Piano Intro]"]),
    (["choir", "chant", "vocals", "humming"], ["[Choir Enters]"]),
    (["ambient", "drone", "atmosphere", "evolving layers"], ["[Ambient Interlude]"]),
    (["strings", "violin", "cello", "orchestral"], ["[String Section]"]),
    (["instrumental", "no vocals", "no lyrics"], ["[Instrumental]", "[Instrumental Break]"]),
]

QUALITY_CONTEXT_RULES = [
    (["boom bap", "old school hip-hop"], ["vinyl crackle", "dusty old recording", "warm low end", "dirty analog texture", "punchy drums"]),
    (["trap", "drill"], ["modern trap mix", "deep 808 bass", "tight low end", "crisp hi-hats", "loud but clean master"]),
    (["ambient", "cinematic"], ["wide stereo space", "long reverb", "deep atmospheric space", "smooth dynamics", "wide dynamic range"]),
    (["horror", "dark ambient"], ["dark cinematic soundscape", "low frequency rumble", "distant echo", "cold airy texture", "no harsh highs"]),
    (["vocal track"], ["clear vocals", "vocal forward mix", "centered lead vocal", "smooth vocal compression", "no buried vocals"]),
    (["lo-fi", "vhs", "tape"], ["lo-fi texture", "tape hiss", "warped tape", "vinyl crackle", "degraded audio"]),
    (["edm", "house", "techno"], ["club-ready mix", "wide stereo", "tight low end", "sidechain compression", "clean high frequencies"]),
]


def smart_generate_prompt(
    selected_tokens: list[str],
    all_data: dict,
    smart_rules: dict,
    app_mode: str = "general",
    active_collection: str | None = None,
    structured_mode: bool = False,
) -> dict:
    """Universally analyze selected tokens and add fitting smart tokens."""
    selected = _dedupe_preserve_order(selected_tokens)
    selected_set = {token.lower() for token in selected}
    app_mode_lower = str(app_mode).strip().lower()
    active_collection_name = str(active_collection or "").strip()

    token_lookup = _build_token_lookup(all_data)
    rule_sets = _normalize_smart_rules(smart_rules)
    limits = {**DEFAULT_SMART_LIMITS, **rule_sets.get("smart_limits", {}), **rule_sets.get("quality_limits", {})}
    structure_pool = _normalize_structure_tags(rule_sets.get("structure_tags_general", DEFAULT_STRUCTURE_TAGS))

    selected_buckets = _bucket_counts(selected, token_lookup)
    selected_instrument_group_counts = _instrument_group_counts(selected, token_lookup)
    selected_contexts = _detect_contexts(selected)
    selected_contexts_lower = {context.lower() for context in selected_contexts}

    added_tokens: List[str] = []
    structure_tags: List[str] = []
    explanations: List[Dict[str, str]] = []
    warnings: List[Dict[str, str]] = []
    reason_parts: List[str] = []

    if not selected:
        return {
            "added_tokens": [],
            "final_tokens": [],
            "structure_tags": [],
            "warnings": [],
            "explanations": [],
            "reason": "Select at least one token first.",
        }

    if active_collection_name:
        reason_parts.append(f"collection: {active_collection_name}")

    if app_mode_lower in {"smart_bgm", "background", "game_background"}:
        reason_parts.append("smart bgm mode")
        _apply_rule_section(
            added_tokens,
            explanations,
            warnings,
            selected_set,
            selected_contexts_lower,
            token_lookup,
            rule_sets.get("mode_rules", {}),
            "smart_bgm",
            limits,
            selected_buckets,
            selected_instrument_group_counts,
            selected,
            section_name="mode_rules",
            app_mode=app_mode_lower,
        )

    _apply_rule_section(
        added_tokens,
        explanations,
        warnings,
        selected_set,
        selected_contexts_lower,
        token_lookup,
        rule_sets.get("global_rules", {}),
        None,
        limits,
        selected_buckets,
        selected_instrument_group_counts,
        selected,
        section_name="global_rules",
        app_mode=app_mode_lower,
    )

    for section_name in ("genre_rules", "mood_rules", "instrument_rules", "vocal_rules", "texture_rules", "performance_rules"):
        section_rules = rule_sets.get(section_name, {})
        if not isinstance(section_rules, dict):
            continue
        _apply_rule_section(
            added_tokens,
            explanations,
            warnings,
            selected_set,
            selected_contexts_lower,
            token_lookup,
            section_rules,
            None,
            limits,
            selected_buckets,
            selected_instrument_group_counts,
            selected,
            section_name=section_name,
            app_mode=app_mode_lower,
        )

    _apply_genre_neighbors(
        added_tokens,
        explanations,
        selected_set,
        token_lookup,
        rule_sets.get("genre_smart_neighbors", {}),
        limits,
        selected,
    )

    _apply_quality_context_rules(
        added_tokens,
        explanations,
        selected_set,
        token_lookup,
        limits,
        selected,
    )

    if active_collection_name:
        collection_rules = rule_sets.get("collection_rules", {})
        if isinstance(collection_rules, dict):
            _apply_rule_section(
                added_tokens,
                explanations,
                warnings,
                selected_set,
                selected_contexts_lower,
                token_lookup,
                collection_rules,
                active_collection_name,
                limits,
                selected_buckets,
                selected_instrument_group_counts,
                selected,
                section_name="collection_rules",
                app_mode=app_mode_lower,
            )

    if structured_mode:
        structure_tags = _select_structure_tags(
            selected,
            selected_set,
            selected_contexts_lower,
            structure_pool,
            limits,
        )
        if structure_tags:
            reason_parts.append("structured mode")

    conflict_warnings = _build_conflict_warnings(rule_sets.get("conflict_rules", []), selected, added_tokens, structure_tags)
    warnings.extend(conflict_warnings)

    final_added = _dedupe_preserve_order(added_tokens)[: int(limits.get("max_total_added", 14))]
    final_structure_tags = _dedupe_preserve_order(structure_tags)[: int(limits.get("max_structure_tags", 3))]
    final_tokens = _dedupe_preserve_order(selected + final_added + final_structure_tags)

    estimated_length = len(", ".join(final_tokens))
    if estimated_length > 280 or len(final_added) >= int(limits.get("max_total_added", 14)):
        warnings.append(
            {
                "type": "overloaded",
                "message_ru": "Промт может быть перегружен. Лучше убрать часть инструментов или настроений.",
                "message_en": "Prompt may be overloaded. Consider removing some instruments or moods.",
            }
        )

    if not reason_parts:
        reason_parts.append("smart generation completed")

    return {
        "added_tokens": final_added,
        "final_tokens": final_tokens,
        "structure_tags": final_structure_tags,
        "warnings": warnings,
        "explanations": explanations,
        "reason": "; ".join(reason_parts),
    }


def _apply_rule_section(
    added_tokens: List[str],
    explanations: List[Dict[str, str]],
    warnings: List[Dict[str, str]],
    selected_set: set[str],
    selected_contexts_lower: set[str],
    token_lookup: Dict[str, Dict[str, str]],
    rules: dict,
    forced_rule_name: str | None,
    limits: dict,
    selected_buckets: Dict[str, int],
    selected_instrument_group_counts: Dict[str, int],
    selected_tokens: List[str],
    *,
    section_name: str,
    app_mode: str,
) -> None:
    if not isinstance(rules, dict):
        return

    avoid_set = {token.lower() for token in selected_tokens}
    added_set = {token.lower() for token in added_tokens}
    used_buckets = dict(selected_buckets)
    used_instrument_groups = dict(selected_instrument_group_counts)

    for rule_name, payload in rules.items():
        if not isinstance(payload, dict):
            continue
        if forced_rule_name is not None and _normalize(rule_name) != _normalize(forced_rule_name):
            continue
        if not _rule_matches(rule_name, section_name, selected_set, selected_contexts_lower, app_mode):
            continue

        add_list = _unique_strings(payload.get("add", []))
        avoid_list = _unique_strings(payload.get("avoid", []))
        if avoid_list:
            avoid_set.update(token.lower() for token in avoid_list)

        matched_source = _best_match_source(rule_name, selected_tokens, selected_contexts_lower, app_mode)
        if not matched_source:
            matched_source = str(rule_name).strip() or section_name

        for token in add_list:
            token_key = token.lower()
            if not token_key or token_key in avoid_set or token_key in selected_set or token_key in added_set:
                continue

            bucket = _bucket_for_token(token_lookup, token)
            category = _category_for_token(token_lookup, token)
            if not _can_add_bucket(bucket, category, used_buckets, used_instrument_groups, limits):
                continue

            added_tokens.append(token)
            added_set.add(token_key)
            used_buckets[bucket] = used_buckets.get(bucket, 0) + 1
            if category.lower().startswith("instrument_"):
                used_instrument_groups[category.lower()] = used_instrument_groups.get(category.lower(), 0) + 1
            explanations.append(
                {
                    "token": token,
                    "reason_ru": _reason_ru(section_name, rule_name, matched_source),
                    "reason_en": _reason_en(section_name, rule_name, matched_source),
                }
            )

            if len(added_tokens) >= int(limits.get("max_total_added", 14)):
                return


def _rule_matches(
    rule_name: str,
    section_name: str,
    selected_set: set[str],
    selected_contexts_lower: set[str],
    app_mode: str,
) -> bool:
    rule = _normalize(rule_name)
    if not rule:
        return False

    if section_name == "global_rules":
        return _text_hits(rule, selected_set) or _global_rule_trigger(rule, selected_set, app_mode)

    if section_name == "mode_rules":
        return _text_hits(rule, selected_set) or _mode_rule_trigger(rule, app_mode)

    if section_name == "collection_rules":
        return _text_hits(rule, selected_set) or _mode_rule_trigger(rule, app_mode)

    return _text_hits(rule, selected_set) or any(rule in context for context in selected_contexts_lower)


def _global_rule_trigger(rule: str, selected_set: set[str], app_mode: str) -> bool:
    if rule in {"instrumental", "vocal track", "beat", "background music", "cinematic soundtrack"}:
        return True if _text_hits(rule, selected_set) else False
    if rule == "background music":
        return any(token in selected_set for token in {"background music", "game background music", "loopable background music"}) or app_mode in {"smart_bgm", "background", "game_background"}
    return False


def _mode_rule_trigger(rule: str, app_mode: str) -> bool:
    mode_tokens = MODE_RULE_ALIASES.get(app_mode, {app_mode})
    return rule in mode_tokens or any(rule in token for token in mode_tokens)


def _best_match_source(rule_name: str, selected_tokens: List[str], selected_contexts_lower: set[str], app_mode: str) -> str:
    rule = _normalize(rule_name)
    for token in selected_tokens:
        if rule and rule in _normalize(token):
            return token
    for context in selected_contexts_lower:
        if rule and (rule in context or context in rule):
            return context
    if app_mode in MODE_RULE_ALIASES and rule in MODE_RULE_ALIASES[app_mode]:
        return app_mode
    return rule_name


def _select_structure_tags(
    selected_tokens: List[str],
    selected_set: set[str],
    selected_contexts_lower: set[str],
    structure_pool: List[Dict[str, str]],
    limits: dict,
) -> List[str]:
    available = {item["en"] for item in structure_pool if item.get("en")}
    chosen: List[str] = []

    for triggers, tags in STRUCTURE_TRIGGER_MAP:
        if any(_contains_any(selected_set, trigger) or any(trigger in context for context in selected_contexts_lower) for trigger in triggers):
            for tag in tags:
                if tag in available and tag not in chosen:
                    chosen.append(tag)

    if len(chosen) > int(limits.get("max_structure_tags", 3)):
        chosen = chosen[: int(limits.get("max_structure_tags", 3))]
    return chosen


def _build_conflict_warnings(conflict_rules: Any, selected_tokens: List[str], added_tokens: List[str], structure_tags: List[str]) -> List[Dict[str, str]]:
    if not isinstance(conflict_rules, list):
        return []

    combined = {token.lower() for token in selected_tokens + added_tokens + structure_tags}
    warnings: List[Dict[str, str]] = []
    seen: set[Tuple[str, str]] = set()

    for rule in conflict_rules:
        if not isinstance(rule, dict):
            continue
        if_contains = {str(item).strip().lower() for item in rule.get("if_contains", []) if str(item).strip()}
        conflicts_with = {str(item).strip().lower() for item in rule.get("conflicts_with", []) if str(item).strip()}
        if not if_contains or not conflicts_with:
            continue

        if if_contains.intersection(combined) and conflicts_with.intersection(combined):
            message_ru = str(rule.get("message_ru", "")).strip()
            message_en = str(rule.get("message_en", "")).strip()
            signature = (message_ru, message_en)
            if signature in seen:
                continue
            seen.add(signature)
            warnings.append({"type": "conflict", "message_ru": message_ru, "message_en": message_en})

    return warnings


def _apply_genre_neighbors(
    added_tokens: List[str],
    explanations: List[Dict[str, str]],
    selected_set: set[str],
    token_lookup: Dict[str, Dict[str, str]],
    neighbor_rules: Any,
    limits: dict,
    selected_tokens: List[str],
) -> None:
    if not isinstance(neighbor_rules, dict):
        return

    added_set = {token.lower() for token in added_tokens}
    selected_and_added = _dedupe_preserve_order(selected_tokens + added_tokens)
    used_buckets = _bucket_counts(selected_and_added, token_lookup)
    used_instrument_groups = _instrument_group_counts(selected_and_added, token_lookup)

    for token in selected_tokens:
        token_key = _normalize(token)
        payload = neighbor_rules.get(token_key)
        if payload is None:
            payload = neighbor_rules.get(token)
        if payload is None:
            continue

        if isinstance(payload, list):
            add_list = _unique_strings(payload)
        elif isinstance(payload, dict):
            add_list = _unique_strings(payload.get("add", []))
        else:
            continue

        for neighbor in add_list:
            n_key = neighbor.lower()
            if not n_key or n_key in selected_set or n_key in added_set:
                continue

            bucket = _bucket_for_token(token_lookup, neighbor)
            category = _category_for_token(token_lookup, neighbor)
            if bucket != "genres":
                continue
            if not _can_add_bucket(bucket, category, used_buckets, used_instrument_groups, limits):
                continue

            added_tokens.append(neighbor)
            added_set.add(n_key)
            used_buckets[bucket] = used_buckets.get(bucket, 0) + 1
            explanations.append(
                {
                    "token": neighbor,
                    "reason_ru": f"добавлен совместимый соседний жанр к {token}",
                    "reason_en": f"added as a compatible neighboring genre to {token}",
                }
            )

            if len(added_tokens) >= int(limits.get("max_total_added", 14)):
                return


def _bucket_counts(selected_tokens: List[str], token_lookup: Dict[str, Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for token in selected_tokens:
        bucket = _bucket_for_token(token_lookup, token)
        counts[bucket] += 1
    return counts


def _instrument_group_counts(selected_tokens: List[str], token_lookup: Dict[str, Dict[str, str]]) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for token in selected_tokens:
        category = _category_for_token(token_lookup, token)
        if category.startswith("instrument_"):
            counts[category] += 1
    return counts


def _can_add_bucket(
    bucket: str,
    category: str,
    used_buckets: Dict[str, int],
    used_instrument_groups: Dict[str, int],
    limits: dict,
) -> bool:
    if bucket == "genres":
        return used_buckets.get(bucket, 0) < int(limits.get("max_genres", 2))
    if bucket == "instruments":
        if used_buckets.get(bucket, 0) >= int(limits.get("max_instruments_total", limits.get("max_instruments", 5))):
            return False
        if category.startswith("instrument_"):
            if used_instrument_groups.get(category, 0) >= int(limits.get("max_instruments_per_group", 2)):
                return False
        if category == "instrument_sound_design_fx":
            if used_instrument_groups.get(category, 0) >= int(limits.get("max_sound_design_fx", 3)):
                return False
        if category in {"instrument_strings_ethnic", "instrument_horror_experimental"}:
            rare_selected = used_instrument_groups.get("instrument_strings_ethnic", 0) + used_instrument_groups.get("instrument_horror_experimental", 0)
            if rare_selected >= int(limits.get("max_rare_instruments", 2)):
                return False
        return True
    if bucket == "vocals":
        return used_buckets.get(bucket, 0) < int(limits.get("max_vocals", 3))
    if bucket == "moods":
        return used_buckets.get(bucket, 0) < int(limits.get("max_moods", 4))
    if bucket == "textures":
        return used_buckets.get(bucket, 0) < int(limits.get("max_textures", 4))
    if bucket == "performance":
        return used_buckets.get(bucket, 0) < int(limits.get("max_performance", 4))
    if bucket == "negative":
        return used_buckets.get(bucket, 0) < int(limits.get("max_negative", 4))
    if bucket == "quality":
        return used_buckets.get(bucket, 0) < int(limits.get("max_quality_tokens_total", 6))
    return True


def _apply_quality_context_rules(
    added_tokens: List[str],
    explanations: List[Dict[str, str]],
    selected_set: set[str],
    token_lookup: Dict[str, Dict[str, str]],
    limits: dict,
    selected_tokens: List[str],
) -> None:
    token_blob = " | ".join(_normalize(token) for token in selected_tokens)
    added_set = {token.lower() for token in added_tokens}
    selected_and_added = _dedupe_preserve_order(selected_tokens + added_tokens)
    used_buckets = _bucket_counts(selected_and_added, token_lookup)
    used_instrument_groups = _instrument_group_counts(selected_and_added, token_lookup)

    for triggers, quality_tokens in QUALITY_CONTEXT_RULES:
        if not any(_normalize(trigger) in token_blob for trigger in triggers):
            continue
        for quality_token in quality_tokens:
            q_key = quality_token.lower()
            if q_key in selected_set or q_key in added_set:
                continue
            bucket = _bucket_for_token(token_lookup, quality_token)
            category = _category_for_token(token_lookup, quality_token)
            if bucket != "quality":
                continue
            if not _can_add_bucket(bucket, category, used_buckets, used_instrument_groups, limits):
                continue

            added_tokens.append(quality_token)
            added_set.add(q_key)
            used_buckets[bucket] = used_buckets.get(bucket, 0) + 1
            explanations.append(
                {
                    "token": quality_token,
                    "reason_ru": "добавлен quality-тег по выбранному стилю",
                    "reason_en": "added quality tag for selected style",
                }
            )


def _bucket_for_token(token_lookup: Dict[str, Dict[str, str]], token: str) -> str:
    category = _category_for_token(token_lookup, token)
    token_text = _normalize(token)

    for needle, bucket in CATEGORY_BUCKETS.items():
        if needle in category or needle in token_text:
            return bucket

    if any(word in token_text for word in ("scratch", "drop", "build", "loop", "background", "structure", "dynamic", "mix", "groove", "tempo", "arrangement")):
        return "performance"
    if any(word in token_text for word in ("no vocals", "no lyrics", "avoid", "not", "without")):
        return "negative"
    return "performance"


def _category_for_token(token_lookup: Dict[str, Dict[str, str]], token: str) -> str:
    lookup = token_lookup.get(_normalize(token), {})
    return str(lookup.get("category", "")).lower()


def _build_token_lookup(all_data: dict) -> Dict[str, Dict[str, str]]:
    lookup: Dict[str, Dict[str, str]] = {}
    if not isinstance(all_data, dict):
        return lookup
    for category, items in all_data.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            en_value = _normalize(str(item.get("en", "")))
            if not en_value:
                continue
            lookup.setdefault(en_value, {"category": str(category)})
    return lookup


def _detect_contexts(tokens: List[str]) -> List[str]:
    token_text = " | ".join(_normalize(token) for token in tokens)
    contexts: List[str] = []
    for context_name, needles in CONTEXT_DEFINITIONS:
        if any(needle in token_text for needle in needles):
            contexts.append(context_name)
    return contexts


def _normalize_smart_rules(smart_rules: dict) -> Dict[str, Any]:
    if not isinstance(smart_rules, dict):
        return {}

    normalized: Dict[str, Any] = {}
    for section in RULE_SECTION_ORDER:
        value = smart_rules.get(section, {})
        if isinstance(value, dict):
            normalized[section] = {
                str(rule_name): _normalize_rule_payload(payload)
                for rule_name, payload in value.items()
                if isinstance(payload, dict) or isinstance(payload, list)
            }
        else:
            normalized[section] = {}

    normalized["conflict_rules"] = _normalize_conflict_rules(smart_rules.get("conflict_rules", []))
    normalized["smart_limits"] = smart_rules.get("smart_limits", {}) if isinstance(smart_rules.get("smart_limits", {}), dict) else {}
    normalized["quality_limits"] = smart_rules.get("quality_limits", {}) if isinstance(smart_rules.get("quality_limits", {}), dict) else {}
    normalized["structure_tags_general"] = _normalize_structure_tags(smart_rules.get("structure_tags_general", DEFAULT_STRUCTURE_TAGS))
    normalized["genre_smart_neighbors"] = smart_rules.get("genre_smart_neighbors", {}) if isinstance(smart_rules.get("genre_smart_neighbors", {}), dict) else {}
    return normalized


def _normalize_rule_payload(payload: Any) -> Dict[str, List[str]]:
    if isinstance(payload, list):
        return {"add": _unique_strings(payload), "avoid": []}
    if not isinstance(payload, dict):
        return {"add": [], "avoid": []}
    return {
        "add": _unique_strings(payload.get("add", [])),
        "avoid": _unique_strings(payload.get("avoid", [])),
    }


def _normalize_conflict_rules(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized: List[Dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        normalized.append(
            {
                "if_contains": _unique_strings(item.get("if_contains", [])),
                "conflicts_with": _unique_strings(item.get("conflicts_with", [])),
                "message_ru": str(item.get("message_ru", "")).strip(),
                "message_en": str(item.get("message_en", "")).strip(),
            }
        )
    return normalized


def _normalize_structure_tags(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        return []
    normalized: List[Dict[str, str]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        en_value = str(item.get("en", "")).strip()
        if not en_value or en_value.lower() in seen:
            continue
        seen.add(en_value.lower())
        normalized.append({"en": en_value, "ru": str(item.get("ru", "")).strip()})
    return normalized


def _unique_strings(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    return _dedupe_preserve_order([str(item).strip() for item in values if str(item).strip()])


def _dedupe_preserve_order(tokens: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for token in tokens:
        normalized = str(token).strip()
        if not normalized:
            continue
        key = normalized.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(normalized)
    return result


def _normalize(text: str) -> str:
    return str(text).strip().lower()


def _text_hits(needle: str, selected_set: set[str]) -> bool:
    needle = _normalize(needle)
    return any(needle in token or token in needle for token in selected_set)


def _contains_any(selected_set: set[str], needle: str) -> bool:
    needle = _normalize(needle)
    return any(needle in token or token in needle for token in selected_set)


def _reason_en(section_name: str, rule_name: str, matched_source: str) -> str:
    source = matched_source.strip() or rule_name
    if section_name == "collection_rules":
        return f"{source} collection was selected"
    return f"{source} was selected"


def _reason_ru(section_name: str, rule_name: str, matched_source: str) -> str:
    source = matched_source.strip() or rule_name
    if section_name == "collection_rules":
        return f"выбрана коллекция {source}"
    return f"выбран {source}"