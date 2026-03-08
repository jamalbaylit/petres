from __future__ import annotations

from typing import Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.patches import Polygon as MplPolygon
import numpy as np

from .....models.boundary import BoundaryPolygon


def _add_boundary_polygon(
    ax: Axes,
    boundary: BoundaryPolygon,
    *,
    facecolor: str | tuple = 'lightblue',
    edgecolor: str | tuple = 'black',
    linewidth: float = 2.0,
    alpha: float = 0.3,
    show_fill: bool = True,
    show_vertices: bool = False,
    **kwargs: Any,
) -> MplPolygon:
    """
    Add a boundary polygon to the 2D plot.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to draw on.
    boundary : BoundaryPolygon
        Boundary polygon to visualize.
    facecolor : str or tuple
        Fill color for the polygon (default: 'lightblue').
    edgecolor : str or tuple
        Edge/border color (default: 'black').
    linewidth : float
        Width of the boundary line (default: 2.0).
    alpha : float
        Transparency of the fill (0-1, default: 0.3).
    show_fill : bool
        Whether to fill the polygon (default: True).
    show_vertices : bool
        Whether to show vertex markers (default: False).
    **kwargs
        Additional kwargs passed to matplotlib Polygon.
    
    Returns
    -------
    polygon : Polygon
        The matplotlib Polygon patch object.
    """
    vertices = boundary.vertices
    
    # Create matplotlib polygon patch
    poly_kwargs = {
        'facecolor': facecolor if show_fill else 'none',
        'edgecolor': edgecolor,
        'linewidth': linewidth,
        'alpha': alpha if show_fill else 1.0,
        **kwargs
    }
    
    polygon = MplPolygon(vertices, closed=True, **poly_kwargs)
    ax.add_patch(polygon)
    
    # Optionally show vertices
    if show_vertices:
        ax.plot(vertices[:, 0], vertices[:, 1], 'o', 
               color=edgecolor, markersize=5, zorder=10)
    
    # Add label if boundary has a name
    if boundary.name:
        # Place label at centroid
        centroid_x = np.mean(vertices[:-1, 0])  # Exclude last point (duplicate of first)
        centroid_y = np.mean(vertices[:-1, 1])
        ax.text(centroid_x, centroid_y, boundary.name,
               ha='center', va='center', fontsize=10,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
    
    return polygon
