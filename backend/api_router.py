from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

try:
    from .controllers.activity_controller import (
        get_favorites,
        get_regions,
        get_search_logs,
        get_visits,
        handle_favorite_delete,
        post_favorite,
        post_region,
        post_visit,
    )
    from .controllers.auth_controller import post_auth_login, post_auth_logout, post_auth_signup
    from .controllers.common import ApiResponse, GetRoute, PostRoute, not_found, payload_route, public_get_route
    from .controllers.recommendation_controller import (
        handle_recommendation_detail,
        handle_recommendation_feedback,
        post_recommendation_search,
    )
    from .controllers.restaurant_controller import post_restaurant_search, post_restaurant_sync
    from .controllers.system_controller import get_config, get_health
    from .controllers.user_controller import post_guest_user
except ImportError:
    from controllers.activity_controller import (
        get_favorites,
        get_regions,
        get_search_logs,
        get_visits,
        handle_favorite_delete,
        post_favorite,
        post_region,
        post_visit,
    )
    from controllers.auth_controller import post_auth_login, post_auth_logout, post_auth_signup
    from controllers.common import ApiResponse, GetRoute, PostRoute, not_found, payload_route, public_get_route
    from controllers.recommendation_controller import (
        handle_recommendation_detail,
        handle_recommendation_feedback,
        post_recommendation_search,
    )
    from controllers.restaurant_controller import post_restaurant_search, post_restaurant_sync
    from controllers.system_controller import get_config, get_health
    from controllers.user_controller import post_guest_user


def handle_get_api(path: str, query: str, cookies: dict[str, str] | None = None) -> ApiResponse | None:
    params = parse_qs(query)
    route = GET_ROUTES.get(path)
    if route is not None:
        return route(params, cookies or {})
    return handle_recommendation_detail(path, cookies or {})


def handle_delete_api(path: str, query: str, cookies: dict[str, str] | None = None) -> ApiResponse | None:
    params = parse_qs(query)
    return handle_favorite_delete(path, params, cookies or {})


def handle_post_api(path: str, payload: dict[str, Any], cookies: dict[str, str] | None = None) -> ApiResponse | None:
    route = POST_ROUTES.get(path)
    if route is not None:
        return route(payload, cookies or {})

    return handle_recommendation_feedback(path, payload, cookies or {})


GET_ROUTES: dict[str, GetRoute] = {
    "/api/health": public_get_route(get_health),
    "/api/config": public_get_route(get_config),
    "/api/regions": public_get_route(get_regions),
    "/api/favorites": get_favorites,
    "/api/search-logs": get_search_logs,
    "/api/visits": get_visits,
}

POST_ROUTES: dict[str, PostRoute] = {
    "/api/auth/signup": post_auth_signup,
    "/api/auth/login": post_auth_login,
    "/api/auth/logout": post_auth_logout,
    "/api/users/guest": post_guest_user,
    "/api/regions": payload_route(201, post_region),
    "/api/recommendations/search": post_recommendation_search,
    "/api/visits": post_visit,
    "/api/restaurants/search": payload_route(200, post_restaurant_search),
    "/api/restaurants/sync": payload_route(201, post_restaurant_sync),
    "/api/favorites": post_favorite,
}