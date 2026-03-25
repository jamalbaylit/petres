from __future__ import annotations

from typing import Any
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from .....models.zone import Zone


def _add_zone(
    ax: Axes,
    zone: Zone,
    *,
    x: np.ndarray,
    y: np.ndarray,
    show_top: bool = True,
    show_base: bool = True,
    show_thickness: bool = False,
    cmap: str = "viridis",
    show_contours: bool = True,
    contour_levels: int = 10,
    show_colorbar: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Add a zone visualization showing top, base, or thickness.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to draw on.
    zone : Zone
        Zone object to visualize.
    x : np.ndarray
        1D array of x coordinates.
    y : np.ndarray
        1D array of y coordinates.
    show_top : bool
        Whether to show top surface (default: True).
    show_base : bool
        Whether to show base surface (default: True).
    show_thickness : bool
        Whether to show thickness map (default: False).
    cmap : str
        Colormap name (default: "viridis").
    show_contours : bool
        Whether to show contour lines (default: True).
    contour_levels : int
        Number of contour levels (default: 10).
    show_colorbar : bool
        Whether to show colorbar (default: True).
    **kwargs
        Additional kwargs passed to pcolormesh or contour.
    
    Returns
    -------
    mesh : QuadMesh or dict
        The matplotlib mesh object(s).
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1D arrays.")
    
    # Sample the zone
    z_top = zone.top.to_grid(x, y)  # (ny, nx)
    z_base = zone.base.to_grid(x, y)  # (ny, nx)
    
    # Create meshgrid
    X, Y = np.meshgrid(x, y)
    
    result = {}
    
    if show_thickness:
        # Show thickness map
        thickness = np.abs(z_base - z_top)
        mesh = ax.pcolormesh(X, Y, thickness, cmap=cmap, shading='auto', **kwargs)
        
        if show_contours:
            contours = ax.contour(X, Y, thickness, levels=contour_levels, 
                                 colors='black', linewidths=0.5, alpha=0.5)
            ax.clabel(contours, inline=True, fontsize=8, fmt='%.0f')
        
        if show_colorbar:
            cbar = plt.colorbar(mesh, ax=ax, label=f'{zone.name} Thickness')
        
        result['thickness'] = mesh
    else:
        # Show top and/or base surfaces
        if show_top:
            contours_top = ax.contour(X, Y, z_top, levels=contour_levels, 
                                     colors='blue', linewidths=1.0)
            ax.clabel(contours_top, inline=True, fontsize=8, fmt='%.0f')
            result['top'] = contours_top
        
        if show_base:
            contours_base = ax.contour(X, Y, z_base, levels=contour_levels, 
                                      colors='red', linewidths=1.0, linestyles='dashed')
            ax.clabel(contours_base, inline=True, fontsize=8, fmt='%.0f')
            result['base'] = contours_base
    
    return result
