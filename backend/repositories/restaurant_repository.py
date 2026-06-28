from __future__ import annotations

import hashlib
from typing import Any

try:
    from ..infra.database import MySQLConnection
    from ..utils import new_id, to_json, utc_now
except ImportError:
    from infra.database import MySQLConnection
    from utils import new_id, to_json, utc_now


def upsert_restaurant(conn: MySQLConnection, restaurant: dict[str, Any]) -> str:
    external_provider = str(restaurant.get("external_provider") or "").strip()
    external_place_id = str(restaurant.get("external_place_id") or restaurant.get("id") or "").strip()
    if not external_provider:
        raise ValueError("restaurant.external_provider is required")
    if not external_place_id:
        raise ValueError("restaurant.external_place_id is required")
    now = utc_now()

    existing = conn.execute(
        """
        SELECT id FROM restaurants
        WHERE external_provider = ? AND external_place_id = ?
        """,
        (external_provider, external_place_id),
    ).fetchone()

    restaurant_id = existing["id"] if existing else new_id()
    values = {
        "id": restaurant_id,
        "external_provider": external_provider,
        "external_place_id": external_place_id,
        "name": str(restaurant.get("name") or "Unknown restaurant").strip(),
        "category": restaurant.get("category"),
        "phone": restaurant.get("phone"),
        "address": restaurant.get("address"),
        "road_address": restaurant.get("road_address"),
        "latitude": restaurant.get("latitude"),
        "longitude": restaurant.get("longitude"),
        "rating": restaurant.get("rating"),
        "review_count": restaurant.get("review_count"),
        "opening_hours": to_json(restaurant.get("opening_hours")),
        "raw_data": to_json(restaurant),
        "last_synced_at": now,
        "created_at": now,
        "updated_at": now,
    }

    if existing:
        conn.execute(
            """
            UPDATE restaurants
            SET name = :name,
                category = :category,
                phone = :phone,
                address = :address,
                road_address = :road_address,
                latitude = :latitude,
                longitude = :longitude,
                rating = :rating,
                review_count = :review_count,
                opening_hours = :opening_hours,
                raw_data = :raw_data,
                last_synced_at = :last_synced_at,
                updated_at = :updated_at
            WHERE id = :id
            """,
            values,
        )
    else:
        conn.execute(
            """
            INSERT INTO restaurants (
              id, external_provider, external_place_id, name, category, phone,
              address, road_address, latitude, longitude, rating, review_count,
              opening_hours, raw_data, last_synced_at, created_at, updated_at
            )
            VALUES (
              :id, :external_provider, :external_place_id, :name, :category, :phone,
              :address, :road_address, :latitude, :longitude, :rating, :review_count,
              :opening_hours, :raw_data, :last_synced_at, :created_at, :updated_at
            )
            """,
            values,
        )

    conn.execute(
        """
        INSERT INTO restaurant_sync_logs (id, restaurant_id, sync_status, created_at, updated_at)
        VALUES (?, ?, 'SUCCESS', ?, ?)
        """,
        (new_id(), restaurant_id, now, now),
    )
    return restaurant_id


def search_cache_key(query: str, longitude: float | None, latitude: float | None, radius: int, sort: str) -> str:
    seed = to_json({
        "provider": "KAKAO",
        "query": query,
        "longitude": longitude,
        "latitude": latitude,
        "radius": radius,
        "sort": sort,
    })
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def save_restaurant_search_snapshot(
    conn: MySQLConnection,
    query: str,
    longitude: float | None,
    latitude: float | None,
    radius: int,
    sort: str,
    requested_pages: int,
    result_count: int,
    is_complete: bool,
    status: str,
    raw_response: dict[str, Any],
    now: str,
) -> None:
    conn.execute(
        """
        INSERT INTO restaurant_search_cache (
          id, cache_key, query, center_latitude, center_longitude, radius, sort,
          requested_pages, result_count, is_complete, status, raw_response,
          synced_at, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE
          requested_pages = VALUES(requested_pages),
          result_count = VALUES(result_count),
          is_complete = VALUES(is_complete),
          status = VALUES(status),
          raw_response = VALUES(raw_response),
          synced_at = VALUES(synced_at),
          updated_at = VALUES(updated_at)
        """,
        (
            new_id(),
            search_cache_key(query, longitude, latitude, radius, sort),
            query,
            latitude,
            longitude,
            radius,
            sort,
            requested_pages,
            result_count,
            1 if is_complete else 0,
            status,
            to_json(raw_response),
            now,
            now,
            now,
        ),
    )