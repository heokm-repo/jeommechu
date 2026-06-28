from __future__ import annotations

import json
from typing import Any

try:
    from ..repositories.activity_repository import insert_recommendation_log
    from ..infra.database import connect
    from ..utils import new_id, parse_json_value, require_text, row_to_dict, utc_now
except ImportError:
    from repositories.activity_repository import insert_recommendation_log
    from infra.database import connect
    from utils import new_id, parse_json_value, require_text, row_to_dict, utc_now


def create_favorite(payload: dict[str, Any]) -> dict[str, Any]:
    user_id = require_text(payload, "user_id")
    restaurant_id = require_text(payload, "restaurant_id")
    search_log_id = payload.get("search_log_id")
    now = utc_now()
    with connect() as conn:
        with conn:
            conn.execute(
                """
                INSERT INTO user_favorites (id, user_id, restaurant_id, memo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE memo = VALUES(memo), updated_at = VALUES(updated_at)
                """,
                (new_id(), user_id, restaurant_id, payload.get("memo"), now, now),
            )
            favorite = conn.execute(
                """
                SELECT id, user_id, restaurant_id, memo, created_at, updated_at
                FROM user_favorites
                WHERE user_id = ? AND restaurant_id = ?
                """,
                (user_id, restaurant_id),
            ).fetchone()

            if search_log_id:
                insert_recommendation_log(
                    conn,
                    search_log_id=search_log_id,
                    log_type="FAVORITE",
                    payload={"user_id": user_id, "restaurant_id": restaurant_id, "favorite_id": favorite["id"] if favorite else None},
                    now=now,
                )
    return {"favorite": row_to_dict(favorite)}


def list_favorites(user_id: str) -> dict[str, Any]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
              uf.id AS favorite_id,
              uf.user_id,
              uf.restaurant_id,
              uf.memo,
              uf.created_at AS favorited_at,
              r.name,
              r.category,
              r.phone,
              r.address,
              r.road_address,
              r.latitude,
              r.longitude,
              r.raw_data
            FROM user_favorites uf
            JOIN restaurants r ON r.id = uf.restaurant_id
            WHERE uf.user_id = ?
            ORDER BY uf.created_at DESC
            """,
            (user_id,),
        ).fetchall()

    favorites = []
    for row in rows:
        item = dict(row)
        raw_data = {}
        try:
            raw_data = parse_json_value(item.pop("raw_data"), {})
        except json.JSONDecodeError:
            item.pop("raw_data", None)
        item["place_url"] = raw_data.get("place_url")
        item["distance"] = raw_data.get("distance")
        favorites.append(item)
    return {"favorites": favorites}


def delete_favorite(user_id: str, restaurant_id: str) -> dict[str, Any]:
    with connect() as conn:
        with conn:
            cursor = conn.execute(
                "DELETE FROM user_favorites WHERE user_id = ? AND restaurant_id = ?",
                (user_id, restaurant_id),
            )
    return {"ok": True, "deleted": cursor.rowcount}