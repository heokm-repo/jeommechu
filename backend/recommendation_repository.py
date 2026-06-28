from __future__ import annotations

try:
    from .repositories.recommendation_repository import *
except ImportError:
    from repositories.recommendation_repository import *