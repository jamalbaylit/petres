from __future__ import annotations

from typing import Any

from matplotlib.axes import Axes
from matplotlib.collections import PathCollection
from matplotlib import patheffects



def _add_well(
    ax: Axes,
    well_x: float,
    well_y: float,
    well_name: str,
    *,
    marker: str = "o",
    marker_size: float = 56.0,
    marker_color: Any = "#b91c1c",
    marker_edgecolor: Any = "white",
    marker_edgewidth: float = 0.9,
    show_label: bool = True,
    label: str | None = None,
    label_fontsize: float = 9.5,
    label_color: Any = "#111827",
    label_offset: tuple[float, float] = (6.0, 6.0),
    zorder: float = 5.0,
    **kwargs: Any,
) -> PathCollection:
    """Add a single vertical well as a 2D marker with an optional label.

    Parameters
    ----------
    ax : Axes
        Target axes.
    well_x : float
        Well x-coordinate.
    well_y : float
        Well y-coordinate.
    well_name : str
        Well name.
    marker : str, default="o"
        Marker style passed to ``Axes.scatter``.
    marker_size : float, default=56.0
        Marker size (points^2).
    marker_color : Any, default="#b91c1c"
        Marker face color.
    marker_edgecolor : Any, default="white"
        Marker edge color.
    marker_edgewidth : float, default=0.9
        Marker edge line width.
    show_label : bool, default=True
        Whether to draw a text label next to the marker.
    label : str | None, default=None
        Explicit label text. Falls back to ``well.name`` when ``None``.
    label_fontsize : float, default=9.5
        Font size for the label text.
    label_color : Any, default="#111827"
        Label text color.
    label_offset : tuple[float, float], default=(6.0, 6.0)
        Label offset in points relative to the marker.
    zorder : float, default=5.0
        Base drawing order for marker and label.
    **kwargs : Any
        Additional keyword arguments forwarded to ``Axes.scatter``.

    Returns
    -------
    PathCollection
        Marker artist returned by ``Axes.scatter``.
    """
    artist = ax.scatter(
        [well_x],
        [well_y],
        marker=marker,
        s=marker_size,
        c=[marker_color],
        edgecolors=[marker_edgecolor],
        linewidths=marker_edgewidth,
        zorder=zorder,
        **kwargs,
    )

    if show_label:
        text = well_name if label is None else label
        if text:
            text_artist = ax.annotate(
                text,
                xy=(well_x, well_y),
                xytext=label_offset,
                textcoords="offset points",
                fontsize=label_fontsize,
                color=label_color,
                ha="left",
                va="bottom",
                zorder=zorder + 1,
            )
            text_artist.set_path_effects(
                [
                    patheffects.withStroke(linewidth=1, foreground="white"),
                    patheffects.Normal(),
                ]
            )

    return artist