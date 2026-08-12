from __future__ import annotations

from typing import Any, Iterable

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
from numpy.typing import NDArray
from typing import Any, Callable, Iterable

from .....config.colors import DEFAULT_CMAP

def _resolve_line_colors(
    cmap: str | None,
    color: str,
    depths: NDArray[Any],
    vmin: float | None,
    vmax: float | None,
) -> tuple[dict[str, Any], Callable[[float], Any] | None]:
    """Work out how contour lines should be colored.

    Returns
    -------
    lc_kwargs : dict
        Keyword arguments to pass straight into ``LineCollection`` (either
        a flat ``colors=`` or a ``cmap=``/``norm=`` pair).
    depth_to_color : callable | None
        Maps a depth value -> RGBA color, for reuse on labels. ``None``
        when using a flat color (labels just reuse ``color`` directly).
    """
    if cmap is None:
        return {"colors": color}, None

    vmin = float(depths.min()) if vmin is None else vmin
    vmax = float(depths.max()) if vmax is None else vmax
    norm = Normalize(vmin=vmin, vmax=vmax)
    colormap = plt.get_cmap(cmap)
    depth_to_color = lambda d: colormap(norm(d))  # noqa: E731

    return {"cmap": cmap, "norm": norm}, depth_to_color


def _add_line_labels(
    ax: Axes,
    segments: list[NDArray[Any]],
    depths: NDArray[Any],
    *,
    depth_to_color: Callable[[float], Any] | None,
    flat_color: str,
    label_color: str | None,
    label_fmt: str,
    label_fontsize: int,
    label_every: int,
) -> None:
    """Annotate every Nth contour line with its depth value.

    Color priority, in order: explicit ``label_color`` override > the
    line's own ``depth_to_color`` (cmap mode) > ``flat_color`` (no cmap).
    """
    step = max(int(label_every), 1)

    for idx in range(0, len(segments), step):
        seg = segments[idx]
        mid = seg[len(seg) // 2]

        if label_color is not None:
            this_color = label_color
        elif depth_to_color is not None:
            this_color = depth_to_color(depths[idx])
        else:
            this_color = flat_color

        ax.annotate(
            label_fmt % depths[idx],
            xy=(mid[0], mid[1]),
            fontsize=label_fontsize,
            color=this_color,
            ha="center",
            va="center",
            bbox={
                "boxstyle": "round,pad=0.1",
                "fc": "white",
                "ec": "none",
                "alpha": 0.7,
            },
        )


def _add_contour_map(
    ax: Axes,
    xy: Iterable[NDArray[Any]],
    z: Iterable[float],
    *,
    cmap: str | None = None,
    color: str = "black",
    # Colorbar Options
    show_colorbar: bool = True,
    colorbar_shrink: float = 0.95,
    colorbar_label: str | None = None,
    # Label Options
    show_labels: bool = True,
    label_fontsize: int = 8,
    label_fmt: str = "%.0f",
    label_color: str | None = 'black',
    label_every: int = 1,
    # Line Options
    linewidth: float = 0.7,
    opacity: float = 0.8,
    vmin: float | None = None,
    vmax: float | None = None,
    **kwargs: Any,
) -> LineCollection:
    """Plot depth-labeled contour lines as a single vectorized line collection.

    Coloring is controlled by a single rule: pass ``cmap`` to color lines
    (and labels) by depth, or leave it ``None`` to use a flat ``color``.
    That one flag is resolved once, up front, and every downstream choice
    (line color, label color, whether to draw a colorbar) just follows it —
    there's no repeated branching later in the function.

    Parameters
    ----------
    ax : Axes
        Target axes where the contours are drawn.
    xy : Iterable[NDArray[Any]]
        Iterable of ``(N_i, 2)`` coordinate arrays, one per contour line.
    z : Iterable[float]
        Iterable of scalar depth values, one per contour line, in the same
        order as ``xy``.
    cmap : str | None, default=None
        Colormap name used to color contour lines by depth. If ``None``,
        all lines/labels use the flat ``color`` argument instead.
    color : str, default='black'
        Solid color used for lines and labels when ``cmap`` is ``None``.
    show_colorbar : bool, default=True
        Whether to draw a colorbar. Only takes effect when ``cmap`` is set.
    colorbar_shrink : float, default=0.95
        Shrink factor passed to ``matplotlib.pyplot.colorbar``.
    colorbar_label : str | None, default=None
        Label for the colorbar.
    show_labels : bool, default=True
        Whether to annotate each contour line with its depth.
    label_fontsize : int, default=8
        Font size used for depth labels.
    label_fmt : str, default="%.0f"
        Format string applied to depth values for labels.
    label_color : str | None, default=None
        Fixed color for every label, overriding the ``cmap``/``color``
        rule above. Leave ``None`` to let labels match their line.
    label_every : int, default=1
        Label every Nth contour line (in input order), to reduce clutter
        when there are many closely-spaced contours.
    linewidth : float, default=0.7
        Line width used for contour lines.
    opacity : float, default=0.8
        Alpha applied to contour lines.
    vmin, vmax : float | None, default=None
        Colormap normalization bounds. Default to min/max of ``z``.
        Ignored when ``cmap`` is ``None``.
    **kwargs : Any
        Additional keyword arguments forwarded to ``LineCollection``.

    Returns
    -------
    LineCollection
        Collection artist created for the contour lines.

    Raises
    ------
    ValueError
        If ``xy`` and ``z`` don't have matching lengths, if there are no
        contour lines, or if any element of ``xy`` isn't shaped ``(N, 2)``.
    """
    segments = [np.asarray(pts, dtype=float) for pts in xy]
    depths = np.asarray(list(z), dtype=float)

    if len(segments) != len(depths):
        raise ValueError(
            f"`xy` and `z` must have the same length, got {len(segments)} and {len(depths)}."
        )
    if not segments:
        raise ValueError("`xy` must contain at least one contour line.")
    for i, seg in enumerate(segments):
        if seg.ndim != 2 or seg.shape[1] != 2:
            raise ValueError(
                f"Each element of `xy` must have shape (N, 2), got {seg.shape} at index {i}."
            )

    # --- 1. Resolve coloring ONCE. Everything else just uses the result. ---
    lc_kwargs, depth_to_color = _resolve_line_colors(cmap, color, depths, vmin, vmax)

    # --- 2. Build & draw the line collection ---
    lc = LineCollection(
        segments,
        linewidths=linewidth,
        alpha=opacity,
        **lc_kwargs,
        **kwargs,
    )
    if depth_to_color is not None:
        lc.set_array(depths)
    ax.add_collection(lc)

    # --- 3. Labels ---
    if show_labels:
        _add_line_labels(
            ax,
            segments,
            depths,
            depth_to_color=depth_to_color,
            flat_color=color,
            label_color=label_color,
            label_fmt=label_fmt,
            label_fontsize=label_fontsize,
            label_every=label_every,
        )

    # --- 4. Colorbar: only ever relevant when a cmap was used ---
    if show_colorbar and depth_to_color is not None:
        cbar = plt.colorbar(lc, ax=ax, shrink=colorbar_shrink)
        if colorbar_label:
            cbar.set_label(colorbar_label)

    ax.autoscale_view()  # add_collection doesn't autoscale on its own
    ax.margins(x=0.0, y=0.0)

    return lc