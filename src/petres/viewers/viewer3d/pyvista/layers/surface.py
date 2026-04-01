from __future__ import annotations

from typing import Any
import pyvista as pv
import numpy as np

from .....models.horizon import Horizon
from ....._utils._color import Color


def _add_surface(
    backend: Any,
    depth: np.ndarray,
    *,
    x: np.ndarray,
    y: np.ndarray,
    name: str | None = None,
    color: Color | None = None,
    scalars: bool | None = True,
    cmap: str | None = None,

    # Colorbar Options
    show_colorbar: bool = True,
    colorbar_title: str | None = None,
    # Contour Options
    show_contours: bool = True,
    contour_levels: int = 10,
    show_contour_labels: bool = True,
    contour_label_fontsize: int = 10,
    contour_opacity: float = 0.8,
    contour_color: str = "black",
    contour_linewidth: float = 3,
    **mesh_kwargs: Any,
) -> pv.StructuredGrid:
    """Add a sampled Horizon surface as a PyVista StructuredGrid.

    Builds a structured grid from regular ``x``/``y`` coordinate arrays and a
    2-D depth array, attaches depth as a point scalar, renders the mesh, and
    optionally overlays iso-contour lines with value labels.

    Parameters
    ----------
    backend : Any
        PyVista viewer instance exposing a ``plotter`` attribute
        (``pyvista.Plotter``).
    depth : np.ndarray
        2-D array of shape ``(len(y), len(x))`` containing depth values.
    x : np.ndarray
        1-D array of x-coordinates.  Ravelled to 1-D if not already.
    y : np.ndarray
        1-D array of y-coordinates.  Ravelled to 1-D if not already.
    name : str or None, optional
        Unique name for the mesh actor inside the plotter.
    color : Color or None, optional
        Solid colour used when ``scalars`` is ``False``.  Ignored when
        ``scalars`` is ``True``.
    scalars : bool or None, default=True
        When ``True`` the surface is coloured by depth values using ``cmap``.
        When ``False`` a solid ``color`` is applied.
    cmap : str or None, optional
        Matplotlib colour-map name.  Defaults to ``"viridis"`` when
        ``scalars`` is ``True``.
    show_colorbar : bool, default=True
        Whether to display a scalar bar (colour-bar) legend.
    colorbar_title : str or None, optional
        Title shown on the colour-bar.  Empty string when ``None``.
    show_contours : bool, default=True
        Whether to overlay iso-contour lines on the surface.
    contour_levels : int, default=10
        Number of evenly-spaced contour iso-values.  Must be at least 1.
    show_contour_labels : bool, default=True
        Whether to place depth-value labels along contour lines.
    contour_label_fontsize : int, default=10
        Font size for contour value labels.
    contour_opacity : float, default=0.8
        Opacity of contour line actors.
    contour_color : str, default="black"
        Colour applied to contour lines and labels.
    contour_linewidth : float, default=3
        Line width of contour actors.
    **mesh_kwargs : Any
        Additional keyword arguments forwarded to
        ``pyvista.Plotter.add_mesh``.

    Returns
    -------
    pv.StructuredGrid
        The constructed PyVista structured grid with depth attached as point
        scalar ``"z"``.

    Raises
    ------
    ValueError
        If ``x`` or ``y`` cannot be reduced to a 1-D array after ravelling.
    ValueError
        If ``depth`` is not 2-D or its shape does not match
        ``(len(y), len(x))``.
    ValueError
        If ``contour_levels`` is less than 1.
    """
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("`x` and `y` must be 1D arrays.")

    if depth.ndim != 2 or depth.shape != (len(y), len(x)):
        raise ValueError(
            f"`depth` must have shape (len(y), len(x)) = {(len(y), len(x))}, got {depth.shape}."
        )

    # Build structured grid
    xx, yy = np.meshgrid(x, y)  # shape: (ny, nx)
    grid = pv.StructuredGrid(xx, yy, depth)

    # Attach scalar data for coloring / contouring
    grid.point_data["z"] = depth.ravel(order="F")
    

    scalar_bar_args = None
    if show_colorbar:
        scalar_bar_args = {
            "title": "" if colorbar_title is None else colorbar_title
        }

    if scalars:
        color = None
        cmap = cmap or "viridis"
        backend.plotter.add_mesh(
            grid,
            name=name,
            scalars="z",
            cmap=cmap,
            scalar_bar_args=scalar_bar_args,
            show_scalar_bar=show_colorbar,
            **mesh_kwargs,
        )
    else:
        backend.plotter.add_mesh(
            grid,
            name=name,
            color=color,
            scalar_bar_args=scalar_bar_args,
            show_scalar_bar=show_colorbar,
            **mesh_kwargs,
        )

    # Contour labels fixed:
    if show_contours:
        zmin = float(np.nanmin(depth))
        zmax = float(np.nanmax(depth))

        if contour_levels < 1:
            raise ValueError("`contour_levels` must be at least 1.")

        contour_values = np.linspace(zmin, zmax, contour_levels)

        contours = grid.contour(
            isosurfaces=contour_values,
            scalars="z",
        )

        backend.plotter.add_mesh(
            contours,
            color=contour_color,
            opacity=contour_opacity,
            line_width=contour_linewidth,
            name=f"{name}_contours" if name else None,
        )

        if show_contour_labels and contours.n_points > 0:
            # Split merged contour output into connected line pieces
            separated = contours.connectivity()

            region_ids = np.unique(separated.cell_data["RegionId"])

            label_points = []
            labels = []

            for region_id in region_ids:
                piece = separated.extract_cells(
                    np.where(separated.cell_data["RegionId"] == region_id)[0]
                )

                if piece.n_points == 0:
                    continue

                pts = piece.points

                # pick a midpoint along this contour piece
                mid_idx = len(pts) // 2
                label_points.append(pts[mid_idx])

                # scalar value should be constant (or nearly constant) on one contour piece
                if "z" in piece.point_data and piece.point_data["z"].size > 0:
                    value = float(np.mean(piece.point_data["z"]))
                else:
                    value = np.nan

                labels.append(f"{value:.2f}")

            if label_points:
                backend.plotter.add_point_labels(
                    np.asarray(label_points),
                    labels,
                    font_size=contour_label_fontsize,
                    text_color=contour_color,
                    shape_opacity=0.0,
                    show_points=False,
                    always_visible=False,
                    name=f"{name}_contour_labels" if name else None,
                )
    return grid