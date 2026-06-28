from __future__ import annotations

from typing import Any

try:
    from ..infra.database import MySQLConnection, connect
    from ..clients import build_kakao_search_params, kakao_place_to_restaurant, kakao_request
    from .location_service import resolve_search_location
    from ..repositories.restaurant_repository import save_restaurant_search_snapshot, upsert_restaurant
    from ..schemas import RestaurantSearchRequest
    from ..utils import utc_now
except ImportError:
    from infra.database import MySQLConnection, connect
    from clients import build_kakao_search_params, kakao_place_to_restaurant, kakao_request
    from location_service import resolve_search_location
    from repositories.restaurant_repository import save_restaurant_search_snapshot, upsert_restaurant
    from schemas import RestaurantSearchRequest
    from utils import utc_now


def collect_kakao_places(
    *,
    query: str,
    address: str,
    longitude: float | None,
    latitude: float | None,
    radius: int,
    sort: str,
    max_pages: int,
    size: int,
) -> dict[str, Any]:
    places: list[dict[str, Any]] = []
    page_payloads: list[dict[str, Any]] = []
    seen_place_ids: set[str] = set()
    source = "/search/keyword.json"
    is_complete = False
    requested_pages = 0

    for page in range(1, max_pages + 1):
        source, params = build_kakao_search_params(query, address, longitude, latitude, radius, sort, page, size)
        kakao_data = kakao_request(source, params)
        requested_pages = page
        documents = kakao_data.get("documents") or []
        meta = kakao_data.get("meta") or {}
        page_payloads.append({"page": page, "params": params, "meta": meta, "place_ids": [item.get("id") for item in documents]})

        for place in documents:
            place_id = str(place.get("id") or "")
            if not place_id or place_id in seen_place_ids:
                continue
            seen_place_ids.add(place_id)
            places.append(place)

        if meta.get("is_end") or not documents:
            is_complete = True
            break

    return {
        "places": places,
        "source": source,
        "page_payloads": page_payloads,
        "requested_pages": requested_pages,
        "is_complete": is_complete,
    }


def restaurant_response_item(restaurant_id: str, restaurant: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": restaurant_id,
        "external_provider": restaurant["external_provider"],
        "external_place_id": restaurant["external_place_id"],
        "name": restaurant["name"],
        "category": restaurant["category"],
        "phone": restaurant["phone"],
        "address": restaurant["address"],
        "road_address": restaurant["road_address"],
        "latitude": restaurant["latitude"],
        "longitude": restaurant["longitude"],
        "place_url": restaurant["place_url"],
        "distance": restaurant["distance"],
    }


def save_kakao_places(conn: MySQLConnection, places: list[dict[str, Any]]) -> list[dict[str, Any]]:
    restaurants = []
    for place in places:
        restaurant = kakao_place_to_restaurant(place)
        restaurant_id = upsert_restaurant(conn, restaurant)
        restaurants.append(restaurant_response_item(restaurant_id, restaurant))
    return restaurants


def search_options(payload: dict[str, Any]) -> dict[str, Any]:
    request = RestaurantSearchRequest.from_payload(payload)
    location = resolve_search_location(request.to_payload())
    return {
        "query": request.query,
        "location": location,
        "address": location["address"],
        "longitude": location["longitude"],
        "latitude": location["latitude"],
        "geocoded": location["geocoded"],
        "radius": request.radius,
        "size": request.size,
        "max_pages": request.pages,
        "sort": request.sort,
    }


def save_search_snapshot_for_result(
    conn: MySQLConnection,
    *,
    options: dict[str, Any],
    search_result: dict[str, Any],
    restaurant_count: int,
    status: str,
    now: str,
) -> None:
    save_restaurant_search_snapshot(
        conn,
        options["query"],
        options["longitude"],
        options["latitude"],
        options["radius"],
        options["sort"],
        search_result["requested_pages"],
        restaurant_count,
        search_result["is_complete"],
        status,
        {"provider": "KAKAO", "source": search_result["source"], "pages": search_result["page_payloads"]},
        now,
    )


def search_and_save_restaurants(payload: dict[str, Any]) -> dict[str, Any]:
    options = search_options(payload)
    search_result = collect_kakao_places(
        query=options["query"],
        address=options["address"],
        longitude=options["longitude"],
        latitude=options["latitude"],
        radius=options["radius"],
        sort=options["sort"],
        max_pages=options["max_pages"],
        size=options["size"],
    )

    status = "SUCCESS" if search_result["places"] else "EMPTY"
    now = utc_now()

    with connect() as conn:
        with conn:
            restaurants = save_kakao_places(conn, search_result["places"])
            save_search_snapshot_for_result(
                conn,
                options=options,
                search_result=search_result,
                restaurant_count=len(restaurants),
                status=status,
                now=now,
            )

    return {
        "provider": "KAKAO",
        "source": "KAKAO_API",
        "cache_hit": False,
        "query": options["query"],
        "address": options["address"] or None,
        "center": {
            "longitude": options["longitude"],
            "latitude": options["latitude"],
            "address_text": options["address"] or (options["geocoded"] or {}).get("address_text"),
        },
        "geocoded": options["geocoded"],
        "meta": {
            "requested_pages": search_result["requested_pages"],
            "result_count": len(restaurants),
            "is_complete": search_result["is_complete"],
            "status": status,
        },
        "restaurants": restaurants,
    }


def restaurant_search(payload: dict[str, Any]) -> dict[str, Any]:
    """Search restaurants from Kakao in real time and persist the response snapshot.

    The DB is intentionally not used as the initial restaurant source for MVP recommendations.
    It stores Kakao snapshots, recommendation history, and user actions.
    """
    return search_and_save_restaurants(payload)