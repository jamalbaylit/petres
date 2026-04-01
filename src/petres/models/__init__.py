"""Geological model primitives for reservoir description.

Exposes the core domain objects used to describe subsurface geometry:
vertical wells with horizon tops and property samples, continuous horizons
fitted from scattered picks, stratigraphic zones bounded by two horizons, and
closed boundary polygons.

Examples
--------
>>> from petres.models import Horizon, Zone, VerticalWell, BoundaryPolygon
"""

from __future__ import annotations

from .wells import VerticalWell
from .horizon import Horizon
from .zone import Zone
from .boundary import BoundaryPolygon


__all__ = [
    "Horizon",
    "Zone",
    "VerticalWell",
    "BoundaryPolygon",
]