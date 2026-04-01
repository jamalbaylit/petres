from __future__ import annotations

from typing import Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Polygon as MplPolygon

from .....models.boundary import BoundaryPolygon


def _polygon_vertices_no_duplicate(vertices: np.ndarray) -> np.ndarray:
    """Return vertices without a duplicated closing point."""
    vertices = np.asarray(vertices, dtype=float)

    if vertices.ndim != 2 or vertices.shape[1] != 2:
        raise ValueError(
            f"`boundary.vertices` must have shape (n, 2), got {vertices.shape}."
        )

    if len(vertices) >= 2 and np.allclose(vertices[0], vertices[-1]):
        return vertices[:-1]

    return vertices



def _add_boundary_polygon(
    ax: Axes,
    boundary: BoundaryPolygon,
    *,
    facecolor: str | tuple = "#7ec8e3",
    edgecolor: str | tuple = "#1f2937",
    linewidth: float = 1.8,
    alpha: float = 0.30,
    show_fill: bool = True,
    show_vertices: bool = False,
    vertex_color: str | tuple | None = None,
    vertex_size: float = 24.0,
    show_label: bool = True,
    label: str | None = None,
    label_fontsize: float = 10.0,
    label_box: bool = True,
    pad_ratio: float = 0.03,
    **kwargs: Any,
) -> MplPolygon:
    """Add a boundary polygon patch to the axes."""
    vertices = _polygon_vertices_no_duplicate(boundary.vertices)

    polygon = MplPolygon(
        vertices,
        closed=True,
        facecolor=facecolor if show_fill else "none",
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha if show_fill else 1.0,
        joinstyle="round",
        capstyle="round",
        antialiased=True,
        **kwargs,
    )
    ax.add_patch(polygon)

    if show_vertices:
        ax.scatter(
            vertices[:, 0],
            vertices[:, 1],
            s=vertex_size,
            c=[edgecolor if vertex_color is None else vertex_color],
            zorder=3,
        )

    polygon_label = label if label is not None else getattr(boundary, "name", None)
    if show_label and polygon_label:
        centroid = vertices.mean(axis=0)
        text_kwargs = {
            "ha": "center",
            "va": "center",
            "fontsize": label_fontsize,
            "zorder": 4,
        }
        if label_box:
            text_kwargs["bbox"] = {
                "boxstyle": "round,pad=0.25",
                "facecolor": "white",
                "edgecolor": "none",
                "alpha": 0.80,
            }

        ax.text(centroid[0], centroid[1], polygon_label, **text_kwargs)

    return polygon