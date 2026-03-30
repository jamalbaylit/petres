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
    """Add a zone visualization showing top/base contours or thickness map."""
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