from __future__ import annotations

try:
    from .services.search_history_service import *
except ImportError:
    from services.search_history_service import *