from __future__ import annotations

from typing import Any

from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh
import matplotlib.pyplot as plt
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
) -> QuadMesh:
    """Add a horizon as a color-mapped surface with optional contours.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to draw onto.
    scalars : np.ndarray
        2D array of shape ``(len(y), len(x))`` with scalar values to plot.
    x : np.ndarray
        1D array of x-coordinates.
    y : np.ndarray
        1D array of y-coordinates.
    cmap : str, optional
        Colormap name, by default ``"viridis"``.
    show_colorbar : bool, optional
        Whether to attach a colorbar, by default ``True``.
    colorbar_shrink : float, optional
        Fractional shrink factor for the colorbar, by default ``0.95``.
    show_contours : bool, optional
        Whether to overlay contour lines, by default ``True``.
    contour_levels : int, optional
        Number of contour levels, by default ``10``.
    show_contour_labels : bool, optional
        Whether to label contour lines, by default ``True``.
    contour_label_fontsize : int, optional
        Font size for contour labels, by default ``8``.
    contour_opacity : float, optional
        Alpha value for contour lines, by default ``0.8``.
    contour_color : str, optional
        Color of contour lines, by default ``"black"``.
    contour_linewidth : float, optional
        Line width of contour lines, by default ``0.7``.
    **kwargs : Any
        Additional keyword arguments forwarded to
        :func:`~matplotlib.axes.Axes.pcolormesh`.

    Returns
    -------
    QuadMesh
        The pcolormesh artist added to *ax*.

    Raises
    ------
    ValueError
        If ``x`` or ``y`` are not 1-D after ravelling, or if ``scalars``
        does not have shape ``(len(y), len(x))``.
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