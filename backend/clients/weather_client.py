from __future__ import annotations

import json
import logging
import math
import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request

try:
    from ..utils import urlopen_direct
except ImportError:
    from utils import urlopen_direct

logger = logging.getLogger(__name__)


def convert_to_grid(lat: float, lon: float) -> tuple[int, int]:
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(
        math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    )
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = (math.pow(sf, sn) * math.cos(slat1)) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = (re * sf) / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = (re * sf) / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    nx = math.floor(ra * math.sin(theta) + XO + 0.5)
    ny = math.floor(ro - ra * math.cos(theta) + YO + 0.5)

    return int(nx), int(ny)


def current_weather_url(api_key: str, lat: float, lon: float) -> str:
    nx, ny = convert_to_grid(lat, lon)
    now = datetime.now(timezone(timedelta(hours=9)))
    if now.minute < 40:
        now = now - timedelta(hours=1)

    safe_key = api_key if "%" in api_key else urllib.parse.quote(api_key, safe="")
    return (
        "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
        f"?serviceKey={safe_key}&pageNo=1&numOfRows=1000&dataType=JSON"
        f"&base_date={now.strftime('%Y%m%d')}&base_time={now.strftime('%H00')}&nx={nx}&ny={ny}"
    )


def describe_precipitation(value: str) -> str:
    return {
        "1": "비",
        "2": "비와 눈",
        "3": "눈",
        "5": "약한 비",
        "6": "약한 비와 눈",
        "7": "약한 눈",
    }.get(value, "맑음/구름")


def parse_weather_items(items: list[dict[str, str]]) -> str | None:
    weather_info = {}
    for item in items:
        category = item.get("category")
        value = item.get("obsrValue")
        if category == "T1H":
            weather_info["temp"] = value
        elif category == "PTY":
            weather_info["pty"] = value
        elif category == "REH":
            weather_info["humidity"] = value

    if not weather_info:
        return None

    parts = []
    if weather_info.get("temp") not in (None, ""):
        parts.append(f"기온 {weather_info['temp']}도")
    if weather_info.get("humidity") not in (None, ""):
        parts.append(f"습도 {weather_info['humidity']}%")
    parts.append(f"날씨상태: {describe_precipitation(weather_info.get('pty', '0'))}")
    return ", ".join(parts)


def get_current_weather(lat: float | None, lon: float | None) -> str:
    if lat is None or lon is None:
        raise ValueError("날씨 조회를 위한 위치 좌표가 없습니다.")
    api_key = os.environ.get("METEO_API_KEY")
    if not api_key:
        raise ValueError("METEO_API_KEY가 설정되어 있지 않습니다. 날씨 정보를 확인할 수 없어 요청을 중단합니다.")

    try:
        req = Request(current_weather_url(api_key, lat, lon))
        with urlopen_direct(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            weather_response = data.get("response", {})
            header = weather_response.get("header", {})
            result_code = header.get("resultCode")
            if result_code and result_code != "00":
                result_message = header.get("resultMsg") or "unknown error"
                raise ValueError(f"Weather API failed: {result_code} {result_message}")

            items = weather_response.get("body", {}).get("items", {}).get("item", [])
            weather_context = parse_weather_items(items)
            if not weather_context:
                raise ValueError("Weather API did not return current weather observations")
            return weather_context
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, AttributeError, KeyError, TypeError, ValueError) as exc:
        logger.warning("Weather API failed: %s", exc)
        raise ValueError(f"날씨 정보를 불러오지 못했습니다: {exc}") from exc