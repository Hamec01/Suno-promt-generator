from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


def merge_prompt_data(existing_data: dict, imported_data: dict) -> dict:
    merged, _, _ = merge_prompt_data_with_stats(existing_data, imported_data)
    return merged


def merge_presets(existing_presets: dict, imported_presets: dict) -> dict:
    merged, _ = merge_presets_with_stats(existing_presets, imported_presets)
    return merged


def merge_user_prompts(existing_prompts: list, imported_prompts: list) -> list:
    merged, _ = merge_user_prompts_with_stats(existing_prompts, imported_prompts)
    return merged


def merge_smart_rules(existing_rules: dict, imported_rules: dict) -> dict:
    merged, _ = merge_smart_rules_with_stats(existing_rules, imported_rules)
    return merged


def merge_prompt_data_with_stats(existing_data: dict, imported_data: dict) -> Tuple[dict, int, int]:
    merged = _normalize_prompt_data(existing_data)
    imported = _normalize_prompt_data(imported_data)

    added_categories = 0
    added_tokens = 0

    for category, imported_items in imported.items():
        if category not in merged:
            merged[category] = []
            added_categories += 1

        existing_items = merged[category]
        seen_en = {
            str(item.get("en", "")).strip().lower()
            for item in existing_items
            if isinstance(item, dict) and str(item.get("en", "")).strip()
        }

        for item in imported_items:
            en_value = str(item.get("en", "")).strip()
            if not en_value:
                continue
            en_key = en_value.lower()
            if en_key in seen_en:
                continue
            new_item = {"en": en_value}
            ru_value = str(item.get("ru", "")).strip()
            if ru_value:
                new_item["ru"] = ru_value
            existing_items.append(new_item)
            seen_en.add(en_key)
            added_tokens += 1

    return merged, added_categories, added_tokens


def merge_presets_with_stats(existing_presets: dict, imported_presets: dict) -> Tuple[dict, int]:
    merged = _normalize_presets(existing_presets)
    imported = _normalize_presets(imported_presets)
    added_count = 0

    for name, tags in imported.items():
        if name not in merged:
            merged[name] = tags
            added_count += 1
            continue

        if merged[name] == tags:
            continue

        index = 2
        while f"{name} ({index})" in merged:
            if merged[f"{name} ({index})"] == tags:
                break
            index += 1

        candidate = f"{name} ({index})"
        if candidate in merged and merged[candidate] == tags:
            continue

        merged[candidate] = tags
        added_count += 1

    return merged, added_count


def merge_user_prompts_with_stats(existing_prompts: list, imported_prompts: list) -> Tuple[list, int]:
    merged = _normalize_user_prompts(existing_prompts)
    imported = _normalize_user_prompts(imported_prompts)

    seen_prompts = {item["prompt"].strip().lower() for item in merged if item.get("prompt")}
    added_count = 0

    for item in imported:
        prompt = item.get("prompt", "").strip()
        if not prompt:
            continue
        key = prompt.lower()
        if key in seen_prompts:
            continue
        if not item.get("created_at"):
            item["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        merged.append(item)
        seen_prompts.add(key)
        added_count += 1

    return merged, added_count


def merge_smart_rules_with_stats(existing_rules: dict, imported_rules: dict) -> Tuple[dict, int]:
    merged = _normalize_smart_rules(existing_rules)
    imported = _normalize_smart_rules(imported_rules)
    added_count = 0

    for section, value in imported.items():
        if section not in merged:
            merged[section] = value
            added_count += 1
            continue

        current_value = merged[section]
        if section == "conflict_rules":
            current_value, section_added = _merge_unique_rule_list(current_value, value)
            merged[section] = current_value
            added_count += section_added
            continue

        if section == "structure_tags_general":
            current_value, section_added = _merge_unique_token_dicts(current_value, value)
            merged[section] = current_value
            added_count += section_added
            continue

        if section == "smart_limits":
            merged[section] = {**current_value, **value}
            continue

        if section == "quality_limits":
            merged[section] = {**current_value, **value}
            continue

        if section == "quality_presets":
            current_value, section_added = _merge_quality_presets(current_value, value)
            merged[section] = current_value
            added_count += section_added
            continue

        if section == "genre_random_rules":
            merged[section] = {**current_value, **value}
            continue

        if section == "genre_smart_neighbors":
            section_added = 0
            for rule_name, rule_values in value.items():
                if rule_name not in current_value:
                    current_value[rule_name] = list(rule_values)
                    section_added += 1
                    continue
                current_value[rule_name] = _merge_unique_strings(list(current_value.get(rule_name, [])), list(rule_values))
            merged[section] = current_value
            added_count += section_added
            continue

        if isinstance(current_value, dict) and isinstance(value, dict):
            section_added = 0
            for rule_name, rule_payload in value.items():
                if rule_name not in current_value:
                    current_value[rule_name] = rule_payload
                    section_added += 1
                    continue
                current_value[rule_name] = _merge_rule_payload(current_value[rule_name], rule_payload)
            merged[section] = current_value
            added_count += section_added

    return merged, added_count


def detect_import_payload(raw: Any) -> Tuple[str, Dict[str, Any]]:
    if isinstance(raw, dict) and any(key in raw for key in ("prompt_data", "presets", "user_prompts")):
        payload = {
            "prompt_data": raw.get("prompt_data", {}),
            "presets": raw.get("presets", {}),
            "user_prompts": raw.get("user_prompts", []),
            "smart_rules": raw.get("smart_rules", {}),
        }
        return "combined", payload

    if isinstance(raw, dict) and any(key in raw for key in ("smart_rules", "global_rules", "mode_rules", "genre_rules", "mood_rules", "instrument_rules", "vocal_rules", "texture_rules", "performance_rules", "collection_rules", "conflict_rules", "smart_limits", "genre_smart_neighbors", "genre_random_rules", "quality_limits", "quality_presets")):
        smart_rules = raw.get("smart_rules", raw)
        return "smart_rules", {"prompt_data": {}, "presets": {}, "user_prompts": [], "smart_rules": smart_rules}

    if _looks_like_prompt_data(raw):
        return "prompt_data", {"prompt_data": raw, "presets": {}, "user_prompts": []}

    if _looks_like_presets(raw):
        return "presets", {"prompt_data": {}, "presets": raw, "user_prompts": []}

    if _looks_like_user_prompts(raw):
        return "user_prompts", {"prompt_data": {}, "presets": {}, "user_prompts": raw}

    return "invalid", {"prompt_data": {}, "presets": {}, "user_prompts": []}


def load_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json_file(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def default_export_filename(prefix: str = "suno_prompt_export") -> str:
    return f"{prefix}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.json"


def build_combined_export(prompt_data: dict, presets: dict, user_prompts: list, smart_rules: dict | None = None) -> dict:
    return {
        "app": "Suno Prompt Generator",
        "version": "1.0",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "prompt_data": prompt_data,
        "presets": presets,
        "user_prompts": user_prompts,
        "smart_rules": smart_rules or {},
    }


def _normalize_prompt_data(data: Any) -> Dict[str, List[Dict[str, str]]]:
    if not isinstance(data, dict):
        return {}
    normalized: Dict[str, List[Dict[str, str]]] = {}
    for category, items in data.items():
        if not isinstance(category, str):
            continue
        if not isinstance(items, list):
            continue
        normalized_items: List[Dict[str, str]] = []
        for item in items:
            if isinstance(item, dict):
                en_value = str(item.get("en", "")).strip()
                if not en_value:
                    continue
                token: Dict[str, str] = {"en": en_value}
                ru_value = str(item.get("ru", "")).strip()
                if ru_value:
                    token["ru"] = ru_value
                normalized_items.append(token)
            elif isinstance(item, str):
                en_value = item.strip()
                if en_value:
                    normalized_items.append({"en": en_value})
        normalized[category] = normalized_items
    return normalized


def _normalize_presets(data: Any) -> Dict[str, List[str]]:
    if not isinstance(data, dict):
        return {}
    normalized: Dict[str, List[str]] = {}
    for name, tags in data.items():
        if not isinstance(name, str):
            continue
        if not isinstance(tags, list):
            continue
        unique_tags: List[str] = []
        seen: set[str] = set()
        for tag in tags:
            tag_text = str(tag).strip()
            if not tag_text or tag_text in seen:
                continue
            unique_tags.append(tag_text)
            seen.add(tag_text)
        normalized[name] = unique_tags
    return normalized


def _normalize_user_prompts(data: Any) -> List[Dict[str, str]]:
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
                "created_at": str(item.get("created_at", "")).strip() or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "description": str(item.get("description", "")).strip(),
            }
        )
    return normalized


def _looks_like_prompt_data(raw: Any) -> bool:
    if not isinstance(raw, dict) or not raw:
        return False
    for _, items in raw.items():
        if not isinstance(items, list):
            return False
        for item in items:
            if isinstance(item, dict):
                if "en" not in item:
                    return False
            elif not isinstance(item, str):
                return False
    return True


def _looks_like_presets(raw: Any) -> bool:
    if not isinstance(raw, dict) or not raw:
        return False
    return all(isinstance(v, list) and all(isinstance(x, str) for x in v) for v in raw.values())


def _looks_like_user_prompts(raw: Any) -> bool:
    if not isinstance(raw, list) or not raw:
        return False
    valid_count = 0
    for item in raw:
        if isinstance(item, dict) and isinstance(item.get("prompt"), str):
            valid_count += 1
    return valid_count > 0


def _normalize_smart_rules(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        return {}

    normalized: Dict[str, Any] = {}
    for section, value in data.items():
        if section in {"global_rules", "mode_rules", "genre_rules", "mood_rules", "instrument_rules", "vocal_rules", "texture_rules", "performance_rules", "collection_rules"}:
            if not isinstance(value, dict):
                continue
            normalized_section: Dict[str, Dict[str, List[str]]] = {}
            for rule_name, payload in value.items():
                normalized_section[str(rule_name)] = _normalize_rule_payload(payload)
            normalized[section] = normalized_section
        elif section == "conflict_rules":
            normalized[section] = _normalize_conflict_rules(value)
        elif section == "structure_tags_general":
            normalized[section] = _normalize_structure_tags(value)
        elif section == "smart_limits":
            normalized[section] = value if isinstance(value, dict) else {}
        elif section == "genre_smart_neighbors":
            if not isinstance(value, dict):
                normalized[section] = {}
                continue
            normalized_neighbors: Dict[str, List[str]] = {}
            for rule_name, payload in value.items():
                if isinstance(payload, list):
                    normalized_neighbors[str(rule_name)] = _unique_string_list(payload)
                elif isinstance(payload, dict):
                    normalized_neighbors[str(rule_name)] = _unique_string_list(payload.get("add", []))
            normalized[section] = normalized_neighbors
        elif section == "genre_random_rules":
            normalized[section] = value if isinstance(value, dict) else {}
        elif section == "quality_limits":
            normalized[section] = value if isinstance(value, dict) else {}
        elif section == "quality_presets":
            normalized[section] = _normalize_quality_presets(value)
        else:
            normalized[section] = value
    return normalized


def _normalize_quality_presets(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        return []
    normalized: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                "name": name,
                "ru": str(item.get("ru", "")).strip(),
                "tokens": _unique_string_list(item.get("tokens", [])),
            }
        )
    return normalized


def _merge_quality_presets(existing: Any, imported: Any) -> Tuple[List[Dict[str, Any]], int]:
    merged = _normalize_quality_presets(existing)
    incoming = _normalize_quality_presets(imported)
    seen = {str(item.get("name", "")).strip().lower() for item in merged}
    added = 0
    for item in incoming:
        key = str(item.get("name", "")).strip().lower()
        if not key or key in seen:
            continue
        merged.append(item)
        seen.add(key)
        added += 1
    return merged, added


def _normalize_rule_payload(payload: Any) -> Dict[str, List[str]]:
    if not isinstance(payload, dict):
        return {"add": [], "avoid": []}
    return {
        "add": _unique_string_list(payload.get("add", [])),
        "avoid": _unique_string_list(payload.get("avoid", [])),
    }


def _merge_rule_payload(existing: Any, imported: Any) -> Dict[str, List[str]]:
    current = _normalize_rule_payload(existing)
    incoming = _normalize_rule_payload(imported)
    return {
        "add": _merge_unique_strings(current["add"], incoming["add"]),
        "avoid": _merge_unique_strings(current["avoid"], incoming["avoid"]),
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
                "if_contains": _unique_string_list(item.get("if_contains", [])),
                "conflicts_with": _unique_string_list(item.get("conflicts_with", [])),
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


def _merge_unique_rule_list(existing: Any, imported: Any) -> Tuple[List[Dict[str, Any]], int]:
    current = _normalize_conflict_rules(existing)
    incoming = _normalize_conflict_rules(imported)
    seen = {
        (tuple(item.get("if_contains", [])), tuple(item.get("conflicts_with", [])), item.get("message_en", ""), item.get("message_ru", ""))
        for item in current
    }
    added = 0
    for item in incoming:
        signature = (tuple(item.get("if_contains", [])), tuple(item.get("conflicts_with", [])), item.get("message_en", ""), item.get("message_ru", ""))
        if signature in seen:
            continue
        current.append(item)
        seen.add(signature)
        added += 1
    return current, added


def _merge_unique_token_dicts(existing: Any, imported: Any) -> Tuple[List[Dict[str, str]], int]:
    current = _normalize_structure_tags(existing)
    incoming = _normalize_structure_tags(imported)
    seen = {item.get("en", "").lower() for item in current if item.get("en")}
    added = 0
    for item in incoming:
        key = item.get("en", "").lower()
        if not key or key in seen:
            continue
        current.append(item)
        seen.add(key)
        added += 1
    return current, added


def _unique_string_list(values: Any) -> List[str]:
    if not isinstance(values, list):
        return []
    return _merge_unique_strings([], [str(item).strip() for item in values if str(item).strip()])


def _merge_unique_strings(existing: List[str], incoming: List[str]) -> List[str]:
    result = list(existing)
    seen = {item.lower() for item in existing}
    for item in incoming:
        key = item.lower()
        if not item or key in seen:
            continue
        result.append(item)
        seen.add(key)
    return result
