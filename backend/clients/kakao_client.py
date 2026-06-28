from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

try:
    from ..utils import parse_float, urlopen_direct
except ImportError:
    from utils import parse_float, urlopen_direct

KAKAO_LOCAL_BASE_URL = "https://dapi.kakao.com/v2/local"
FOOD_CATEGORY_GROUP_CODE = "FD6"


def kakao_request(path: str, params: dict[str, Any]) -> dict[str, Any]:
    rest_api_key = os.environ.get("KAKAO_REST_API_KEY")
    if not rest_api_key:
        raise ValueError("KAKAO_REST_API_KEY가 설정되어 있지 않습니다. Kakao 검색을 대체하지 않고 요청을 중단합니다.")

    cleaned_params = {key: value for key, value in params.items() if value not in (None, "")}
    url = f"{KAKAO_LOCAL_BASE_URL}{path}?{urlencode(cleaned_params)}"
    request = Request(url, headers={"Authorization": f"KakaoAK {rest_api_key}"})

    try:
        with urlopen_direct(request, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Kakao Local API failed: HTTP {exc.code} {detail}") from exc
    except URLError as exc:
        raise ValueError(f"Kakao Local API connection failed: {exc.reason}") from exc


def geocode_address(address: str) -> dict[str, Any]:
    data = kakao_request("/search/address.json", {"query": address, "size": 1})
    documents = data.get("documents") or []
    if not documents:
        raise ValueError(f"주소를 찾지 못했습니다: {address}. 예: 서울 강남구 역삼동처럼 시/구/동을 포함해 입력해 주세요.")
    document = documents[0]
    return {
        "address_text": document.get("address_name"),
        "longitude": parse_float(document.get("x")),
        "latitude": parse_float(document.get("y")),
        "raw": document,
    }


def kakao_place_to_restaurant(place: dict[str, Any]) -> dict[str, Any]:
    return {
        "external_provider": "KAKAO",
        "external_place_id": place.get("id"),
        "name": place.get("place_name"),
        "category": place.get("category_name"),
        "phone": place.get("phone"),
        "address": place.get("address_name"),
        "road_address": place.get("road_address_name"),
        "latitude": parse_float(place.get("y")),
        "longitude": parse_float(place.get("x")),
        "rating": None,
        "review_count": None,
        "raw_data": place,
        "place_url": place.get("place_url"),
        "distance": place.get("distance"),
    }


def build_kakao_search_params(
    query: str,
    address: str,
    longitude: float | None,
    latitude: float | None,
    radius: int,
    sort: str,
    page: int,
    size: int,
) -> tuple[str, dict[str, Any]]:
    has_center = longitude is not None and latitude is not None
    if has_center and query in ("", "음식점", "식당", "맛집"):
        return "/search/category.json", {
            "category_group_code": FOOD_CATEGORY_GROUP_CODE,
            "x": longitude,
            "y": latitude,
            "radius": radius,
            "sort": sort,
            "page": page,
            "size": size,
        }

    keyword = query if not address else f"{address} {query}"
    return "/search/keyword.json", {
        "query": keyword,
        "category_group_code": FOOD_CATEGORY_GROUP_CODE,
        "x": longitude,
        "y": latitude,
        "radius": radius if has_center else None,
        "sort": sort if has_center else "accuracy",
        "page": page,
        "size": size,
    }