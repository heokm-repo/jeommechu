from __future__ import annotations

from typing import Any

try:
    from ..repositories.activity_repository import recommendation_restaurant_from_row
    from ..infra.database import connect
    from ..utils import parse_json_value, row_to_dict
except ImportError:
    from repositories.activity_repository import recommendation_restaurant_from_row
    from infra.database import connect
    from utils import parse_json_value, row_to_dict


def list_search_logs(user_id: str, limit: int = 30) -> dict[str, Any]:
    with connect() as conn:
        rows = conn.execute(
            """
            SELECT
              sl.id,
              sl.user_id,
              sl.latitude,
              sl.longitude,
              sl.address_text,
              sl.emotion_state,
              sl.search_context,
              sl.created_at,
              COUNT(sr.id) AS recommendation_count,
              MAX(CASE WHEN sr.recommendation_rank = 1 THEN r.name END) AS top_restaurant_name,
              MAX(CASE WHEN sr.recommendation_rank = 1 THEN sr.ai_reason END) AS top_ai_reason
            FROM search_logs sl
            LEFT JOIN search_recommendations sr ON sr.search_log_id = sl.id
            LEFT JOIN restaurants r ON r.id = sr.restaurant_id
            WHERE sl.user_id = ?
            GROUP BY sl.id
            ORDER BY sl.created_at DESC
            LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return {"search_logs": [dict(row) for row in rows]}


def get_search_owner_user_id(search_log_id: str) -> str | None:
    with connect() as conn:
        search = conn.execute("SELECT user_id FROM search_logs WHERE id = ?", (search_log_id,)).fetchone()
    if not search:
        return None
    return search["user_id"]

def get_search(search_log_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        search = conn.execute("SELECT * FROM search_logs WHERE id = ?", (search_log_id,)).fetchone()
        if not search:
            return None
        recommendations = conn.execute(
            """
            SELECT
              sr.id,
              sr.recommendation_rank,
              sr.score,
              sr.ai_reason,
              r.id AS restaurant_id,
              r.external_provider,
              r.external_place_id,
              r.name,
              r.category,
              r.phone,
              r.address,
              r.road_address,
              r.latitude,
              r.longitude,
              r.raw_data
            FROM search_recommendations sr
            JOIN restaurants r ON r.id = sr.restaurant_id
            WHERE sr.search_log_id = ?
            ORDER BY sr.recommendation_rank ASC
            """,
            (search_log_id,),
        ).fetchall()
        recommendation_log = conn.execute(
            """
            SELECT payload
            FROM recommendation_logs
            WHERE search_log_id = ? AND log_type = 'SEARCH'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (search_log_id,),
        ).fetchone()

    log_payload = parse_json_value(recommendation_log["payload"] if recommendation_log else None, {})
    weather_context = log_payload.get("weather_context") if isinstance(log_payload, dict) else None
    response_recommendations = []
    for row in recommendations:
        item = dict(row)
        item["restaurant"] = recommendation_restaurant_from_row(item)
        response_recommendations.append(item)

    return {
        "search": row_to_dict(search),
        "weather_context": weather_context,
        "recommendations": response_recommendations,
    }