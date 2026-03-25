from __future__ import annotations

from importlib.util import find_spec

HAS_MATPLOTLIB = find_spec("matplotlib") is not None