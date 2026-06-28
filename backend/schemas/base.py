from __future__ import annotations

from typing import Any

try:
    from ..utils import clamp_int, parse_float
except ImportError:
    from utils import clamp_int, parse_float


def optional_text(payload: dict[str, Any], key: str, default: str = "") -> str:
    return str(payload.get(key) or default).strip()


def required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' is required")
    return value.strip()


def optional_float(payload: dict[str, Any], key: str) -> float | None:
    return parse_float(payload.get(key))


def bounded_int(payload: dict[str, Any], key: str, default: int, minimum: int, maximum: int) -> int:
    return clamp_int(payload.get(key), default, minimum, maximum)


def string_list(value: Any) -> list[str]:
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        value = [value]

    normalized = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized