from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

import numpy as np
import pyvista as pv





def _add_well(
    backend,
    *,
    well_x: float,
    well_y: float,
    well_top: float | None,
    well_bottom: float | None,
    well_name: str,
    label_font_size: float=15,
    label_color: Any='black',
    line_color: Any='black',
    line_width: float=3.0,
) -> None:
    """Render well tubes and labels in a 3D scene.

    Parameters
    ----------
    backend
        Viewer backend exposing a PyVista plotter and optional deferred
        point-label API.
    well_x : float
        Well x-coordinate in scene units.
    well_y : float
        Well y-coordinate in scene units.
    well_top : float | None
        Top z-coordinate of the well. If ``None``, a fallback is inferred
        from plot bounds.
    well_bottom : float | None
        Bottom z-coordinate of the well. If ``None``, a fallback is inferred
        from plot bounds.
    well_name : str
        Label text displayed at the well top location.
    label_font_size : float, default=12
        Font size used for the well label.
    label_color : Any, default='black'
        Text color for the well label.
    line_color : Any, default='black'
        Color used to render the well tube.
    line_width : float, default=1.0
        Tube radius used when rendering the well line.
    """
    p = backend.plotter


    if well_top is None or well_bottom is None:
        bounds = p.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
        z_min, z_max = bounds[4], bounds[5]
        # Add a small margin so the tube visually extends beyond the data
        margin = abs(z_max - z_min) * 0.05 if z_max != z_min else 1.0
        fallback_top = z_max + margin
        fallback_bottom = z_min - margin
        well_top = well_top if well_top is not None else fallback_top
        well_bottom = well_bottom if well_bottom is not None else fallback_bottom


    # line = pv.Line((well_x, well_y, well_top), (well_x, well_y, well_bottom))
    # tube = line.tube(radius=line_width, n_sides=16, capping=True)
    # p.add_mesh(tube, color=line_color, smooth_shading=True)
    p.add_lines(
        np.array([[well_x, well_y, well_top],
                [well_x, well_y, well_bottom]]),
        color=line_color,
        width=line_width,  # always visible
    )
        

    # label_pos = (well_x * t.xscale, well_y * t.yscale, (well_top - z_offset) * t.zscale)
    label_pos = (well_x, well_y, well_top)
    point_labels = np.asarray([label_pos])
    labels = [well_name]
    label_kwargs = dict(
        font_size=label_font_size,
        text_color=label_color, bold=True, shadow=True,
        always_visible=False, show_points=False,
        shape_opacity=1,
        shape=None,
    )
    defer_labels = getattr(backend, "_defer_point_labels", None)
    if callable(defer_labels):
        defer_labels(point_labels, labels, **label_kwargs)
    else:
        backend.plotter.add_point_labels(
            point_labels,
            labels,
            **label_kwargs,
        )