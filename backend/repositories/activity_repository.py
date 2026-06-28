from __future__ import annotations

from typing import Any

try:
    from ..utils import new_id, parse_json_value, to_json
except ImportError:
    from utils import new_id, parse_json_value, to_json


def insert_recommendation_log(
    conn: Any,
    *,
    search_log_id: str,
    log_type: str,
    payload: dict[str, Any],
    now: str,
    log_id: str | None = None,
) -> str:
    created_log_id = log_id or new_id()
    conn.execute(
        """
        INSERT INTO recommendation_logs (id, search_log_id, log_type, payload, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (created_log_id, search_log_id, log_type, to_json(payload), now, now),
    )
    return created_log_id


def recommendation_restaurant_from_row(item: dict[str, Any]) -> dict[str, Any]:
    raw_data = parse_json_value(item.pop("raw_data"), {})
    return {
        "id": item.pop("restaurant_id"),
        "external_provider": item.pop("external_provider"),
        "external_place_id": item.pop("external_place_id"),
        "name": item.pop("name"),
        "category": item.pop("category"),
        "phone": item.pop("phone"),
        "address": item.pop("address"),
        "road_address": item.pop("road_address"),
        "latitude": item.pop("latitude"),
        "longitude": item.pop("longitude"),
        "place_url": raw_data.get("place_url"),
        "distance": raw_data.get("distance"),
    }