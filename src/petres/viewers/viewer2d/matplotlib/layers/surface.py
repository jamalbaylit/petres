from __future__ import annotations


from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh
from numpy.typing import NDArray

def _add_surface(
    ax: Axes,
    scalars: NDArray[Any],
    *,
    x: NDArray[Any],
    y: NDArray[Any],

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
) -> QuadMesh:
    """Plot a scalar surface with optional contour overlays.

    Parameters
    ----------
    ax : Axes
        Target axes where the surface is drawn.
    scalars : NDArray[Any]
        Scalar values on a 2D grid with shape ``(len(y), len(x))``.
    x : NDArray[Any]
        X coordinates convertible to a one-dimensional float array.
    y : NDArray[Any]
        Y coordinates convertible to a one-dimensional float array.
    cmap : str, default="viridis"
        Colormap name used for the surface.
    show_colorbar : bool, default=True
        Whether to draw a colorbar for the generated mesh.
    colorbar_shrink : float, default=0.95
        Shrink factor passed to ``matplotlib.pyplot.colorbar``.
    show_contours : bool, default=True
        Whether to draw contour lines on top of the surface.
    contour_levels : int, default=10
        Number of contour levels.
    show_contour_labels : bool, default=True
        Whether to render labels on contour lines.
    contour_label_fontsize : int, default=8
        Font size used for contour labels.
    contour_opacity : float, default=0.8
        Opacity applied to contour lines.
    contour_color : str, default="black"
        Color used for contour lines.
    contour_linewidth : float, default=0.7
        Line width used for contour lines.
    **kwargs : Any
        Additional keyword arguments forwarded to ``Axes.pcolormesh``.

    Returns
    -------
    QuadMesh
        Mesh artist created by ``Axes.pcolormesh``.

    Raises
    ------
    ValueError
        If ``x`` or ``y`` are not one-dimensional after conversion, or if
        ``scalars`` does not match shape ``(len(y), len(x))``.
    """
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