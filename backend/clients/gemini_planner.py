from __future__ import annotations

import json
import logging
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request

try:
    from ..utils import parse_json_value, urlopen_direct
except ImportError:
    from utils import parse_json_value, urlopen_direct

logger = logging.getLogger(__name__)


def postposition_eul_reul(word: str) -> str:
    if not word:
        return "을"
    last_char = word[-1]
    if 0xAC00 <= ord(last_char) <= 0xD7A3:
        return "을" if (ord(last_char) - 0xAC00) % 28 != 0 else "를"
    return "을(를)"


def build_query_planning_prompt(payload: dict[str, Any], emotion_state: str, weather_context: str | None) -> str:
    search_context = str(payload.get("search_context") or "").strip()
    contexts = payload.get("contexts") or []
    weather_text = f"\n- 현재 날씨: {weather_context}" if weather_context else ""
    return f"""
사용자의 상태(감정, 상황, 태그) 및 요청 문맥을 분석하여, 카카오맵 장소 검색 API에 입력할 최적의 음식점 검색어(단어 1개)를 기획하세요.

[규칙]
1. 사용자가 특정 음식이나 메뉴(예: 샌드위치, 떡볶이)를 명시했다면 반드시 그 메뉴를 검색어로 선정하세요.
2. 구체적인 메뉴가 없다면 감정이나 식사 상황(예: 혼밥, 스트레스)에 가장 잘 어울리는 음식 키워드 1개를 도출하세요.
3. 결과는 반드시 한국어 메뉴명 또는 음식 종류 키워드 단어 1개여야 합니다. (예: "부대찌개", "일식")
4. 마크다운 없이 JSON만 응답하세요.

입력:
- 사용자 입력 문맥: {search_context}
- 감정 상태 태그: {emotion_state}
- 식사 상황/스타일 태그: {contexts}{weather_text}

응답 형식:
{{"query":"김치찌개"}}
"""


def plan_kakao_search_query(payload: dict[str, Any], emotion_state: str, weather_context: str | None = None) -> dict[str, Any]:
    explicit_query = str(payload.get("query") or "").strip()
    if explicit_query:
        return {
            "query": explicit_query,
            "model_name": "user-provided-query",
            "reason": "사용자가 직접 입력한 Kakao 검색어입니다.",
            "keywords": [explicit_query],
        }

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되어 있지 않습니다. 이 서비스는 대체 추천을 생성하지 않으므로 요청을 중단합니다.")

    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    data = {
        "contents": [{"parts": [{"text": build_query_planning_prompt(payload, emotion_state, weather_context)}]}],
        "generationConfig": {"response_mime_type": "application/json"},
    }

    try:
        req = Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urlopen_direct(req, timeout=8) as response:
            result = json.loads(response.read().decode("utf-8"))
            text_response = result["candidates"][0]["content"]["parts"][0]["text"].strip()
        parsed = parse_json_value(text_response, {})
        query = str(parsed.get("query") or "").strip()[:40]
        if not query:
            raise ValueError("Gemini did not return a query")
        keywords = parsed.get("keywords") if isinstance(parsed.get("keywords"), list) else [query]

        reason = parsed.get("reason")
        if not reason:
            reason = f"Gemini가 당신을 위한 검색어로 '{query}'{postposition_eul_reul(query)} 선택했습니다."

        return {
            "query": query,
            "model_name": model,
            "reason": reason,
            "keywords": [str(item).strip() for item in keywords if str(item).strip()],
            "raw_response": parsed,
        }
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        logger.warning("Gemini query planning failed: %s", exc)
        raise ValueError(f"Gemini query planning failed: {exc}") from exc


def extracted_keywords_for(
    payload: dict[str, Any],
    emotion_state: str,
    query: str,
    planned_keywords: list[str] | None = None,
) -> list[dict[str, str]]:
    keywords = [
        {"keyword": emotion_state, "keyword_type": "MOOD"},
        {"keyword": query, "keyword_type": "FOOD_TYPE"},
    ]
    for planned_keyword in planned_keywords or []:
        if planned_keyword and planned_keyword not in {item["keyword"] for item in keywords}:
            keywords.append({"keyword": planned_keyword, "keyword_type": "FOOD_TYPE"})
    for context in payload.get("contexts") or []:
        if isinstance(context, str) and context.strip():
            keywords.append({"keyword": context.strip(), "keyword_type": "SITUATION"})
    address = str(payload.get("address") or "").strip()
    if address:
        keywords.append({"keyword": address, "keyword_type": "PLACE_TYPE"})
    return keywords