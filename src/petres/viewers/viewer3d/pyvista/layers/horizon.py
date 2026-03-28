from __future__ import annotations

from typing import Any
from pyparsing import Optional
import pyvista as pv
import numpy as np

from .....models.horizon import Horizon
from ....._utils._color import Color


def _add_horizon(
    backend,
    horizon: Horizon,
    *,
    x: np.ndarray,
    y: np.ndarray,
    name: str | None = None,
    color: Optional[Color] = None,
    scalars: Optional[bool] = True,   
    cmap: Optional[str] = None,             
    **mesh_kwargs: Any,
) -> pv.StructuredGrid:
    """
    Add a sampled Horizon surface as a PyVista StructuredGrid.

    Notes
    -----
    - Vectorized: uses Horizon.to_grid(x, y) which samples in one shot.
    - Produces a surface grid; you can control appearance via mesh_kwargs
      passed to plotter.add_mesh (e.g., color, opacity, show_edges, cmap...).
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1D arrays.")

    z = horizon.to_grid(x, y)  # (ny, nx)

    # Build 2D meshgrid for X/Y matching Z shape
    xx, yy = np.meshgrid(x, y)  # both (ny, nx)

    grid = pv.StructuredGrid(xx, yy, z)

    if scalars is True:
        grid.point_data['z'] = z.ravel(order="F")
        color = None  # use scalars + cmap for coloring
        cmap = cmap or "viridis"

    backend.plotter.add_mesh(grid, name=name, color=color, cmap=cmap, **mesh_kwargs)
    return grid