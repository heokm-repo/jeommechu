from __future__ import annotations

try:
    from .services.recommendation_service import *
except ImportError:
    from services.recommendation_service import *