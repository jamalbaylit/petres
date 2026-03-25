from __future__ import annotations

from typing import Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from .....models.horizon import Horizon


def _add_horizon(
    ax: Axes,
    horizon: Horizon,
    *,
    x: np.ndarray,
    y: np.ndarray,
    cmap: str = "viridis",
    show_contours: bool = True,
    contour_levels: int = 10,
    show_colorbar: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Add a horizon as a color-mapped surface with optional contours.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to draw on.
    horizon : Horizon
        Horizon object to visualize.
    x : np.ndarray
        1D array of x coordinates.
    y : np.ndarray
        1D array of y coordinates.
    cmap : str
        Colormap name (default: "viridis").
    show_contours : bool
        Whether to show contour lines (default: True).
    contour_levels : int
        Number of contour levels (default: 10).
    show_colorbar : bool
        Whether to show colorbar (default: True).
    **kwargs
        Additional kwargs passed to pcolormesh.
    
    Returns
    -------
    mesh : QuadMesh
        The matplotlib mesh object.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1D arrays.")
    
    # Sample the horizon
    z = horizon.to_grid(x, y)  # (ny, nx)
    
    # Create meshgrid
    X, Y = np.meshgrid(x, y)
    
    # Plot the surface
    mesh = ax.pcolormesh(X, Y, z, cmap=cmap, shading='auto', **kwargs)
    
    # Add contours if requested
    if show_contours:
        contours = ax.contour(X, Y, z, levels=contour_levels, colors='black', 
                             linewidths=0.5, alpha=0.5)
        ax.clabel(contours, inline=True, fontsize=8, fmt='%.0f')
    
    # Colorbar
    if show_colorbar:
        cbar = plt.colorbar(mesh, ax=ax, label=f'{horizon.name} Depth')
    
    return mesh
