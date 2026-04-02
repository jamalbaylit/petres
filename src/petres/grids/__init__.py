"""Grid classes for structured petroleum reservoir modeling.

Exposes 2D rectilinear, pillar, and corner-point grid representations along
with a generic grid-property container.

Examples
--------
>>> from petres.grids import Rectilinear2DGrid, GridProperty
>>> import numpy as np
>>> grid = Rectilinear2DGrid(
...     x_vertex=np.linspace(0, 1000, 11),
...     y_vertex=np.linspace(0, 500, 6),
...     active=np.ones((5, 10), dtype=bool),
... )
>>> prop = GridProperty(name="PORO", values=np.full(grid.cell_shape, 0.2))
"""

from __future__ import annotations

from .rectilinear import Rectilinear2DGrid
from .cornerpoint import CornerPointGrid
from .properties import GridProperty
from .pillar import PillarGrid

__all__ = [
    "Rectilinear2DGrid", 
    "PillarGrid", 
    "CornerPointGrid",
    "GridProperty",
]