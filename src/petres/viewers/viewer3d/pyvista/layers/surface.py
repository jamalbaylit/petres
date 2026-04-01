from __future__ import annotations

from typing import Any
from pyparsing import Optional
import pyvista as pv
import numpy as np

from .....models.horizon import Horizon
from ....._utils._color import Color


def _add_surface(
    backend,
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
    """
    Add a sampled Horizon surface as a PyVista StructuredGrid.

    Parameters
    ----------
    show_contours : bool, default=True
        Whether to overlay contour lines on the horizon surface.
    contour_levels : int, default=10
        Number of contour levels.
    show_contour_labels : bool, default=True
        Whether to place contour value labels on the contour lines.
    contour_label_fontsize : int, default=8
        Font size of contour labels.
    contour_opacity : float, default=0.8
        Opacity of contour lines.
    contour_color : str, default="black"
        Color of contour lines and labels.
    contour_linewidth : float, default=0.7
        Width of contour lines.
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