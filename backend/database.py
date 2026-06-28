from __future__ import annotations

try:
    from .infra.database import *
except ImportError:
    from infra.database import *
