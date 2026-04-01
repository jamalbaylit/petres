from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

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
    show_contour_labels: bool = False,
    show_colorbar: bool = True,
    colorbar_shrink: float = 0.95,
    top_color: str = "#2563eb",
    base_color: str = "#dc2626",
    top_linewidth: float = 1.0,
    base_linewidth: float = 1.0,
    base_linestyle: str = "--",
    thickness_contour_color: str = "black",
    thickness_contour_linewidth: float = 0.6,
    **kwargs: Any,
) -> dict[str, Any]:
    """Add a zone visualization showing top/base contours or thickness map.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to draw on.
    zone : Zone
        Stratigraphic zone containing top and base horizons.
    x : np.ndarray
        1D array of x-coordinates (easting). Must be 1D after ravelling.
    y : np.ndarray
        1D array of y-coordinates (northing). Must be 1D after ravelling.
    show_top : bool, default True
        Whether to draw top-horizon contours when not in thickness mode.
    show_base : bool, default True
        Whether to draw base-horizon contours when not in thickness mode.
    show_thickness : bool, default False
        When ``True``, render a color-mapped thickness map instead of
        top/base contours.
    cmap : str, default 'viridis'
        Colormap name used for the thickness pcolormesh.
    show_contours : bool, default True
        Whether to overlay contour lines on the thickness map.
    contour_levels : int, default 10
        Number of contour levels.
    show_contour_labels : bool, default False
        Whether to annotate contour lines with their values.
    show_colorbar : bool, default True
        Whether to attach a color bar to the thickness mesh.
    colorbar_shrink : float, default 0.95
        Fractional size of the color bar relative to the axes.
    top_color : str, default '#2563eb'
        Line color for top-horizon contours.
    base_color : str, default '#dc2626'
        Line color for base-horizon contours.
    top_linewidth : float, default 1.0
        Line width for top-horizon contours.
    base_linewidth : float, default 1.0
        Line width for base-horizon contours.
    base_linestyle : str, default '--'
        Line style for base-horizon contours.
    thickness_contour_color : str, default 'black'
        Color for contour lines drawn over the thickness map.
    thickness_contour_linewidth : float, default 0.6
        Line width for thickness-map contour lines.
    **kwargs : Any
        Extra keyword arguments forwarded to ``ax.pcolormesh``.

    Returns
    -------
    dict[str, Any]
        Mapping of artist names to Matplotlib objects.  Possible keys:
        ``'thickness'``, ``'thickness_contours'``, ``'top'``, ``'base'``.

    Raises
    ------
    ValueError
        If ``x`` or ``y`` are not 1D after ravelling.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("`x` and `y` must be 1D arrays.")

    z_top = zone.top.to_grid(x, y)
    z_base = zone.base.to_grid(x, y)
    X, Y = np.meshgrid(x, y, indexing="xy")

    result: dict[str, Any] = {}

    if show_thickness:
        thickness = z_base - z_top

        mesh = ax.pcolormesh(
            X,
            Y,
            thickness,
            cmap=cmap,
            shading="auto",
            **kwargs,
        )
        result["thickness"] = mesh

        if show_contours:
            contours = ax.contour(
                X,
                Y,
                thickness,
                levels=contour_levels,
                colors=thickness_contour_color,
                linewidths=thickness_contour_linewidth,
                alpha=0.55,
            )
            result["thickness_contours"] = contours

            if show_contour_labels:
                ax.clabel(contours, inline=True, fontsize=8, fmt="%.0f")

        if show_colorbar:
            cbar = plt.colorbar(mesh, ax=ax, shrink=colorbar_shrink)
            # cbar.set_label(colorbar_label or f"{zone.name} thickness")

    else:
        if show_top:
            contours_top = ax.contour(
                X,
                Y,
                z_top,
                levels=contour_levels,
                colors=top_color,
                linewidths=top_linewidth,
            )
            result["top"] = contours_top

            if show_contour_labels:
                ax.clabel(contours_top, inline=True, fontsize=8, fmt="%.0f")

        if show_base:
            contours_base = ax.contour(
                X,
                Y,
                z_base,
                levels=contour_levels,
                colors=base_color,
                linewidths=base_linewidth,
                linestyles=base_linestyle,
            )
            result["base"] = contours_base

            if show_contour_labels:
                ax.clabel(contours_base, inline=True, fontsize=8, fmt="%.0f")

    return result