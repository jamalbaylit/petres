"""Compatibility flags for optional dependencies."""

from __future__ import annotations

from importlib.util import find_spec

HAS_MATPLOTLIB: bool = find_spec("matplotlib") is not None
"""Whether matplotlib is available in the current environment."""