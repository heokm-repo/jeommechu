from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any
from urllib.request import Request, ProxyHandler, build_opener


class HttpError(Exception):
    status_code = 500

    def __init__(self, message: str | None = None):
        super().__init__(message or "Request failed")


class AuthenticationError(HttpError):
    status_code = 401

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message)


class AuthorizationError(HttpError):
    status_code = 403

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message)

def urlopen_direct(req: Request | str, timeout: float = 8.0) -> Any:
    handler = ProxyHandler({})
    opener = build_opener(handler)
    return opener.open(req, timeout=timeout)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")


def new_id() -> str:
    return str(uuid.uuid4())


def to_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False)


def parse_json_value(value: Any, default: Any = None) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def parse_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def clamp_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def require_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"'{key}' is required")
    return value.strip()


def row_to_dict(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)