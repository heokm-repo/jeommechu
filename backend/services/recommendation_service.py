from __future__ import annotations

from typing import Any

try:
    from ..infra.database import connect
    from ..clients import extracted_keywords_for, get_current_weather, plan_kakao_search_query
    from .location_service import resolve_search_location
    from ..repositories.recommendation_repository import (
        ensure_guest_user,
        insert_ai_response,
        insert_keywords,
        insert_recommendation_log,
        insert_search_log,
        save_search_recommendations,
    )
    from .restaurant_service import restaurant_search
    from ..schemas import RecommendationSearchRequest
    from ..utils import to_json, utc_now
except ImportError:
    from infra.database import connect
    from clients import extracted_keywords_for, get_current_weather, plan_kakao_search_query
    from services.location_service import resolve_search_location
    from repositories.recommendation_repository import (
        ensure_guest_user,
        insert_ai_response,
        insert_keywords,
        insert_recommendation_log,
        insert_search_log,
        save_search_recommendations,
    )
    from services.restaurant_service import restaurant_search
    from schemas import RecommendationSearchRequest
    from utils import to_json, utc_now


def create_recommendation_search(payload: dict[str, Any]) -> dict[str, Any]:
    request = RecommendationSearchRequest.from_payload(payload)
    normalized_payload = request.to_payload()
    emotion_state = request.emotion_state

    location = resolve_search_location(normalized_payload)
    search_payload = {
        **normalized_payload,
        "address": location["address"],
        "longitude": location["longitude"],
        "latitude": location["latitude"],
    }

    weather_context = get_current_weather(location["latitude"], location["longitude"])
    query_plan = plan_kakao_search_query(search_payload, emotion_state, weather_context)
    query = query_plan["query"]
    ai_reason = query_plan.get("reason") or f"'{emotion_state}' 상황에 어울리는 '{query}' 맛집입니다."
    restaurant_result = restaurant_search({**search_payload, "query": query})
    restaurants = (restaurant_result.get("restaurants") or [])[:10]
    center = restaurant_result.get("center") or {}
    keywords = extracted_keywords_for(search_payload, emotion_state, query, query_plan.get("keywords") or [])
    now = utc_now()

    with connect() as conn:
        with conn:
            user_id = ensure_guest_user(conn, request.user_id)
            search_log_id = insert_search_log(
                conn,
                user_id=user_id,
                latitude=center.get("latitude"),
                longitude=center.get("longitude"),
                address_text=center.get("address_text") or restaurant_result.get("address"),
                emotion_state=emotion_state,
                search_context=request.search_context,
                now=now,
            )

            insert_ai_response(
                conn,
                search_log_id=search_log_id,
                model_name=query_plan.get("model_name") or "unknown",
                prompt_text=to_json({"task": "emotion_menu_mapping", "input": search_payload, "weather_context": weather_context}),
                response_text=query_plan,
                now=now,
            )
            insert_keywords(conn, search_log_id, keywords, now)
            saved_recommendations = save_search_recommendations(
                conn,
                search_log_id=search_log_id,
                restaurants=restaurants,
                ai_reason=ai_reason,
                now=now,
            )
            insert_recommendation_log(
                conn,
                search_log_id=search_log_id,
                payload={"request": search_payload, "query": query, "query_plan": query_plan, "weather_context": weather_context},
                now=now,
            )

    return {
        "user_id": user_id,
        "search_log_id": search_log_id,
        "emotion_state": emotion_state,
        "query": query,
        "source": restaurant_result.get("source"),
        "cache_hit": restaurant_result.get("cache_hit"),
        "center": center,
        "meta": restaurant_result.get("meta"),
        "weather_context": weather_context,
        "keywords": keywords,
        "recommendations": saved_recommendations,
    }