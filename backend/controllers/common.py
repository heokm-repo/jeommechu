from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from ..utils import clamp_int
except ImportError:
    from utils import clamp_int

ApiResponse = tuple[int, dict[str, Any]] | tuple[int, dict[str, Any], dict[str, str]]
QueryParams = dict[str, list[str]]
GetRoute = Callable[[QueryParams, dict[str, str]], ApiResponse]
SimpleGetRoute = Callable[[QueryParams], ApiResponse]
PostRoute = Callable[[dict[str, Any], dict[str, str]], ApiResponse]
PayloadHandler = Callable[[dict[str, Any]], dict[str, Any]]
NoPayloadHandler = Callable[[], dict[str, Any]]


def not_found() -> ApiResponse:
    return 404, {"error": "Not found"}


def require_query_param(params: QueryParams, key: str) -> str:
    value = (params.get(key) or [""])[0].strip()
    if not value:
        raise ValueError(f"{key} is required")
    return value


def limited_query_value(params: QueryParams, key: str = "limit", default: int = 30) -> int:
    return clamp_int((params.get(key) or [default])[0], default, 1, 100)


def public_get_route(handler: SimpleGetRoute) -> GetRoute:
    def route(params: QueryParams, _cookies: dict[str, str]) -> ApiResponse:
        return handler(params)

    return route


def payload_route(status: int, handler: PayloadHandler) -> PostRoute:
    def route(payload: dict[str, Any], _cookies: dict[str, str]) -> ApiResponse:
        return status, handler(payload)

    return route


def no_payload_route(status: int, handler: NoPayloadHandler) -> PostRoute:
    def route(_payload: dict[str, Any], _cookies: dict[str, str]) -> ApiResponse:
        return status, handler()

    return route