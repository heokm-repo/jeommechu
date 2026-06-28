from __future__ import annotations

import os

from .common import ApiResponse, QueryParams


def get_health(_params: QueryParams) -> ApiResponse:
    return 200, {"ok": True}


def get_config(_params: QueryParams) -> ApiResponse:
    return 200, {"kakao_js_api_key": os.environ.get("KAKAO_JS_API_KEY")}