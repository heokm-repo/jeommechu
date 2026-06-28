from __future__ import annotations

from typing import Any

from .common import ApiResponse, QueryParams, limited_query_value, require_query_param

try:
    from ..services.activity_service import (
        create_favorite,
        create_region,
        create_visit,
        delete_favorite,
        get_search_owner_user_id,
        list_favorites,
        list_regions,
        list_search_logs,
        list_visits,
    )
    from ..services.auth_service import SESSION_COOKIE_NAME, require_session_owner
    from ..utils import AuthorizationError
except ImportError:
    from services.activity_service import (
        create_favorite,
        create_region,
        create_visit,
        delete_favorite,
        get_search_owner_user_id,
        list_favorites,
        list_regions,
        list_search_logs,
        list_visits,
    )
    from services.auth_service import SESSION_COOKIE_NAME, require_session_owner
    from utils import AuthorizationError


def session_token(cookies: dict[str, str]) -> str | None:
    return cookies.get(SESSION_COOKIE_NAME)


def require_query_owner(params: QueryParams, cookies: dict[str, str]) -> str:
    user_id = require_query_param(params, "user_id")
    return require_session_owner(session_token(cookies), user_id)


def require_payload_owner(payload: dict[str, Any], cookies: dict[str, str]) -> str:
    return require_session_owner(session_token(cookies), payload.get("user_id"))


def require_owned_search_log(search_log_id: Any, user_id: str) -> None:
    if not search_log_id:
        return
    owner_user_id = get_search_owner_user_id(str(search_log_id))
    if owner_user_id is None:
        raise ValueError("'search_log_id' was not found")
    if owner_user_id != user_id:
        raise AuthorizationError("You can only attach actions to your own search logs")


def get_regions(_params: QueryParams) -> ApiResponse:
    return 200, list_regions()


def get_favorites(params: QueryParams, cookies: dict[str, str]) -> ApiResponse:
    user_id = require_query_owner(params, cookies)
    return 200, list_favorites(user_id)


def get_search_logs(params: QueryParams, cookies: dict[str, str]) -> ApiResponse:
    user_id = require_query_owner(params, cookies)
    return 200, list_search_logs(user_id, limited_query_value(params))


def get_visits(params: QueryParams, cookies: dict[str, str]) -> ApiResponse:
    user_id = require_query_owner(params, cookies)
    return 200, list_visits(user_id, limited_query_value(params))


def handle_favorite_delete(path: str, params: QueryParams, cookies: dict[str, str]) -> ApiResponse | None:
    if not path.startswith("/api/favorites/"):
        return None

    restaurant_id = path.rsplit("/", 1)[-1]
    user_id = require_query_owner(params, cookies)
    return 200, delete_favorite(user_id, restaurant_id)


def post_region(payload: dict[str, Any]) -> dict[str, Any]:
    return create_region(payload)


def post_visit(payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    user_id = require_payload_owner(payload, cookies)
    require_owned_search_log(payload.get("search_log_id"), user_id)
    return 201, create_visit(payload)


def post_favorite(payload: dict[str, Any], cookies: dict[str, str]) -> ApiResponse:
    user_id = require_payload_owner(payload, cookies)
    require_owned_search_log(payload.get("search_log_id"), user_id)
    return 201, create_favorite(payload)