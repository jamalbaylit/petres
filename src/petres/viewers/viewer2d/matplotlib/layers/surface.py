from __future__ import annotations


from matplotlib.axes import Axes
import matplotlib.pyplot as plt
from typing import Any
import numpy as np

def _add_surface(
    ax: Axes,
    scalars: np.ndarray,
    *,
    x: np.ndarray,
    y: np.ndarray,

    cmap: str = "viridis",
    # Colorbar Options
    show_colorbar: bool = True,
    colorbar_shrink: float = 0.95,
    
    # Countour Options
    show_contours: bool = True,
    contour_levels: int = 10,
    show_contour_labels: bool = True,
    contour_label_fontsize: int = 8,
    contour_opacity: float = 0.8,
    contour_color: str = "black",
    contour_linewidth: float = 0.7,
    **kwargs: Any,
) -> Any:
    """Add a horizon as a color-mapped surface with optional contours."""
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("`x` and `y` must be 1D arrays.")
    
    if scalars.ndim != 2 or scalars.shape != (len(y), len(x)):
        raise ValueError(
            f"`scalars` must have shape (len(y), len(x)) = {(len(y), len(x))}, got {scalars.shape}."
        )
    
    X, Y = np.meshgrid(x, y, indexing="xy")

    mesh = ax.pcolormesh(
        X,
        Y,
        scalars,
        cmap=cmap,
        shading="auto",
        **kwargs,
    )

    if show_contours:
        contours = ax.contour(
            X,
            Y,
            scalars,
            levels=contour_levels,
            colors=contour_color,
            linewidths=contour_linewidth,
            alpha=contour_opacity,
        )
        if show_contour_labels:
            ax.clabel(contours, inline=True, fontsize=contour_label_fontsize, fmt="%.0f")

    if show_colorbar:
        cbar = plt.colorbar(mesh, ax=ax, shrink=colorbar_shrink)
        # cbar.set_label(colorbar_label or f"{horizon.name} Depth")
    return mesh