from __future__ import annotations

try:
    from .infra.static_files import *
except ImportError:
    from infra.static_files import *
