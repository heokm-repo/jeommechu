from __future__ import annotations

try:
    from .infra.static_server import *
except ImportError:
    from infra.static_server import *
