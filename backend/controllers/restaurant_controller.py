from __future__ import annotations

from typing import Any

try:
    from ..services.restaurant_service import restaurant_search, search_and_save_restaurants
except ImportError:
    from services.restaurant_service import restaurant_search, search_and_save_restaurants


def post_restaurant_search(payload: dict[str, Any]) -> dict[str, Any]:
    return restaurant_search(payload)


def post_restaurant_sync(payload: dict[str, Any]) -> dict[str, Any]:
    return search_and_save_restaurants(payload)