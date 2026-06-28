from __future__ import annotations

try:
    from .services.feedback_service import *
except ImportError:
    from services.feedback_service import *