from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray
from matplotlib.axes import Axes
from matplotlib.patches import Polygon as MplPolygon

from .....models.boundary import BoundaryPolygon


def _polygon_vertices_no_duplicate(vertices: ArrayLike) -> NDArray[np.float64]:
    """Remove a duplicated closing vertex from a polygon.

    Parameters
    ----------
    vertices : ArrayLike
        Polygon vertices expected to be coercible to shape ``(n, 2)``.

    Returns
    -------
    numpy.typing.NDArray[numpy.float64]
        Vertices as a float array, excluding the last point when it repeats
        the first point.

    Raises
    ------
    ValueError
        If the coerced vertices array does not have shape ``(n, 2)``.
    """
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
    facecolor: str | tuple[float, ...] = "#7ec8e3",
    edgecolor: str | tuple[float, ...] = "#1f2937",
    linewidth: float = 1.8,
    alpha: float = 0.30,
    show_fill: bool = True,
    show_vertices: bool = False,
    vertex_color: str | tuple[float, ...] | None = None,
    vertex_size: float = 24.0,
    show_label: bool = True,
    label: str | None = None,
    label_fontsize: float = 10.0,
    label_box: bool = True,
    pad_ratio: float = 0.03,
    **kwargs: Any,
) -> MplPolygon:
    """Add a boundary polygon patch to a Matplotlib axes.

    Parameters
    ----------
    ax : Axes
        Target axes where the polygon patch is added.
    boundary : BoundaryPolygon
        Boundary object providing polygon vertices and optional ``name``.
    facecolor : str | tuple[float, ...], default="#7ec8e3"
        Fill color used when ``show_fill`` is enabled.
    edgecolor : str | tuple[float, ...], default="#1f2937"
        Polygon edge color.
    linewidth : float, default=1.8
        Edge line width in points.
    alpha : float, default=0.30
        Fill opacity used when ``show_fill`` is enabled.
    show_fill : bool, default=True
        Whether to render polygon fill.
    show_vertices : bool, default=False
        Whether to draw vertex markers.
    vertex_color : str | tuple[float, ...] | None, default=None
        Vertex marker color. Uses ``edgecolor`` when ``None``.
    vertex_size : float, default=24.0
        Vertex marker size passed to ``Axes.scatter`` as ``s``.
    show_label : bool, default=True
        Whether to annotate the polygon centroid with a label.
    label : str | None, default=None
        Explicit label text. Falls back to ``boundary.name`` when ``None``.
    label_fontsize : float, default=10.0
        Font size used for label text.
    label_box : bool, default=True
        Whether to draw a rounded white box behind the label.
    pad_ratio : float, default=0.03
        Reserved keyword-only argument forwarded for API compatibility.
    **kwargs : Any
        Additional keyword arguments forwarded to ``matplotlib.patches.Polygon``.

    Returns
    -------
    matplotlib.patches.Polygon
        The polygon patch added to ``ax``.
    """
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