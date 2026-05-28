from __future__ import annotations

from typing import Dict, Iterable, List


def build_prompt_parts(
    track_type: str,
    selected_by_category: Dict[str, List[str]],
    category_order: Iterable[str],
) -> List[str]:
    """Build ordered unique prompt parts based on selected tags."""
    seen: set[str] = set()
    parts: List[str] = []

    def add_part(value: str) -> None:
        if not value:
            return
        normalized = value.strip()
        if not normalized:
            return
        if normalized.lower() == "no vocals":
            return
        if normalized in seen:
            return
        seen.add(normalized)
        parts.append(normalized)

    add_part(track_type)

    for category in category_order:
        for value in selected_by_category.get(category, []):
            add_part(value)

    return parts


def build_prompt(
    track_type: str,
    selected_by_category: Dict[str, List[str]],
    category_order: Iterable[str],
) -> str:
    return ", ".join(build_prompt_parts(track_type, selected_by_category, category_order))


def build_short_prompt(parts: Iterable[str], max_length: int = 120) -> str:
    """Build short prompt without cutting words in the middle."""
    short_parts: List[str] = []

    for part in parts:
        candidate = ", ".join(short_parts + [part]) if short_parts else part
        if len(candidate) <= max_length:
            short_parts.append(part)
        else:
            break

    return ", ".join(short_parts)
