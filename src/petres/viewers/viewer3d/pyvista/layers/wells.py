from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol

import numpy as np
import pyvista as pv

from ..._core.theme import SceneTheme3D


class _BackendLike(Protocol):
    plotter: pv.Plotter


class _ViewerLike(Protocol):
    theme: SceneTheme3D


class _WellLike(Protocol):
    x: float
    y: float
    top: float
    bottom: float
    name: str

def _add_wells(
    backend: _BackendLike,
    viewer: _ViewerLike,
    wells: Sequence[_WellLike],
    *,
    color: Any | None = None,
) -> None:
    """Render well tubes and labels in a 3D scene.

    Parameters
    ----------
    backend : _BackendLike
        Rendering backend exposing a PyVista plotter.
    viewer : _ViewerLike
        Viewer context exposing the active scene theme.
    wells : Sequence[_WellLike]
        Wells to render. Each well must provide ``x``, ``y``, ``top``,
        ``bottom``, and ``name`` attributes.
    color : Any, optional
        Override for the well line color. If omitted, the theme color is used.
    """
    p = backend.plotter
    t = viewer.theme

    well_color = color or t.well_line_color
    avg_len = float(np.mean([w.bottom - w.top for w in wells])) if wells else 0.0
    z_offset = avg_len * 0.05

    for w in wells:
        line = pv.Line((w.x, w.y, w.top), (w.x, w.y, w.bottom))
        tube = line.tube(radius=t.well_line_width, n_sides=16, capping=True)
        p.add_mesh(tube, color=well_color, smooth_shading=True)

        label_pos = (w.x * t.xscale, w.y * t.yscale, (w.top - z_offset) * t.zscale)
        p.add_point_labels(
            [label_pos], [w.name],
            font_size=t.wells_label_font_size,
            text_color="white", bold=True, shadow=True,
            always_visible=True, show_points=False,
            shape_opacity=1,
        )
