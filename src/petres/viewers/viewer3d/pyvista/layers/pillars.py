from __future__ import annotations

from typing import Any
import numpy as np
import pyvista as pv
from ....._utils._colors import Color


# ----------------------------------------------------------------------
# Colour helpers
# ----------------------------------------------------------------------
def _plotter_background(plotter: pv.Plotter) -> tuple[float, float, float]:
    """Read the plotter background as a unit RGB triple.

    Fallback only: the viewer passes its theme background explicitly, since
    it applies the theme to the plotter at render time, after layers have
    been added.
    """
    return tuple(plotter.background_color.float_rgb)


def _fade(rgb: tuple, amount: float, background: tuple) -> tuple:
    """Blend ``rgb`` toward ``background`` by ``amount`` in [0, 1].

    Used instead of transparency: a dense set of translucent lines renders
    order-dependently, which produces dark blotches wherever lines happen to
    draw back-to-front. Blending the colour is order-independent and gives
    the same visual weight.
    """
    amount = float(min(max(amount, 0.0), 1.0))
    return tuple((1.0 - amount) * c + amount * b for c, b in zip(rgb, background))


# ----------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------
def _sample_indices(n: int, target: int) -> np.ndarray:
    """Pick at most ``target`` evenly spaced indices from ``range(n)``.

    The first and last indices are always kept so the silhouette stays
    closed, and the step is exactly constant wherever that is possible.

    Even spacing has to be exact, not near-exact. Spreading ``target``
    indices over ``n - 1`` intervals by rounding gives gaps that differ by
    one index, which sounds harmless but reads as alternating wide/narrow
    columns -- 12 pillars over 50 cells alternates 5, 4, 5, 4. So the number
    of gaps is reduced to the largest divisor of ``n - 1`` that is no larger
    than ``target - 1``, giving a constant step. Rounding is used only when
    no usable divisor exists (a prime interval count), where the alternative
    would be collapsing to two pillars at the ends.
    """
    if n <= 1 or target <= 0:
        return np.arange(max(n, 0))
    if target == 1:
        return np.array([0, n - 1], dtype=np.int64)
    if n <= target:
        return np.arange(n)

    intervals = n - 1
    max_gaps = target - 1
    # Refuse a divisor that would thin the pillars below a third of the
    # requested count; a near-even grid beats a nearly empty one.
    floor_gaps = max(2, -(-max_gaps // 3))
    for gaps in range(max_gaps, floor_gaps - 1, -1):
        if intervals % gaps == 0:
            return np.arange(0, n, intervals // gaps, dtype=np.int64)

    return np.unique(np.linspace(0, n - 1, target).round().astype(np.int64))


def _polylines(paths) -> pv.PolyData | None:
    """Build a PolyData holding one polyline cell per path.

    Polylines rather than independent segments: with
    ``render_lines_as_tubes`` the renderer can then join consecutive
    sections instead of butting flat-capped quads against each other.
    """
    paths = [np.asarray(p, dtype=np.float64) for p in paths]
    paths = [p for p in paths if p.ndim == 2 and p.shape[0] >= 2]
    if not paths:
        return None

    pts = np.concatenate(paths, axis=0)
    conn = np.empty(sum(len(p) + 1 for p in paths), dtype=np.int64)

    write = 0
    offset = 0
    for p in paths:
        m = len(p)
        conn[write] = m
        conn[write + 1 : write + 1 + m] = np.arange(offset, offset + m)
        write += m + 1
        offset += m

    return pv.PolyData(pts, lines=conn)


def _lattice_lines(
    points: np.ndarray,
    jj: np.ndarray | None = None,
    ii: np.ndarray | None = None,
) -> pv.PolyData | None:
    """Grid lines of a lattice, optionally restricted to selected rows/columns.

    Each line keeps the full node resolution along its own direction, so a
    coarse cage still follows curved geometry instead of cutting corners
    between the sampled nodes.

    Parameters
    ----------
    points : np.ndarray
        (nj+1, ni+1, 3) array of lattice node coordinates.
    jj : np.ndarray, optional
        Row indices to draw along i. Defaults to every row.
    ii : np.ndarray, optional
        Column indices to draw along j. Defaults to every column.
    """
    nj, ni = points.shape[:2]
    if jj is None:
        jj = np.arange(nj)
    if ii is None:
        ii = np.arange(ni)

    paths = [points[j, :, :] for j in jj]
    paths += [points[:, i, :] for i in ii]
    return _polylines(paths)


def _segments(start: np.ndarray, end: np.ndarray) -> pv.PolyData:
    """Build a PolyData of independent 2-point line cells."""
    n = start.shape[0]
    pts = np.empty((2 * n, 3), dtype=np.float64)
    pts[0::2] = start
    pts[1::2] = end

    conn = np.empty((n, 3), dtype=np.int64)
    conn[:, 0] = 2
    conn[:, 1] = np.arange(0, 2 * n, 2)
    conn[:, 2] = np.arange(1, 2 * n, 2)

    return pv.PolyData(pts, lines=conn.ravel())


# ----------------------------------------------------------------------
# Main entry point
# ----------------------------------------------------------------------
def _add_pillars(
    plotter: pv.Plotter,
    pillar_top: np.ndarray,
    pillar_bottom: np.ndarray,
    color: str = "black",
    line_width: float = 2.0,
    show_grid_lines: bool = True,
    show_pillars: bool = True,
    show_arrows: bool = False,
    pillar_opacity: float = 0.5,
    max_pillars_per_axis: int | None = None,
    opacity: float = 1.0,
    lattice_mode: str = "both",
    base_fade: float = 0.45,
    texture_fade: float = 0.75,
    use_fade: bool = True,
    background: Any | None = None,
    render_lines_as_tubes: bool = True,
    **kwargs,
) -> None:
    """Render a pillar grid as a skeletal wireframe.

    Draws the top and base lattices as i/j grid lines with the pillars
    connecting them, so the grid structure reads directly.

    Every pillar is drawn by default. On a fine grid that can render the
    volume as an opaque mass; ``max_pillars_per_axis`` thins them to an
    evenly spaced subset, and the lattice is then drawn twice -- a strong
    cage on exactly the rows and columns that carry a pillar, over a faded
    full-resolution lattice -- so every visible pillar sits on a visible
    intersection rather than on an arbitrary node. The base lattice is
    always lighter and thinner than the top, which separates the two in
    projection instead of letting them moire against each other.

    Parameters
    ----------
    plotter : pv.Plotter
        The PyVista plotter to add the pillars to.
    pillar_top : np.ndarray
        (nj+1, ni+1, 3) array of pillar top coordinates.
    pillar_bottom : np.ndarray
        (nj+1, ni+1, 3) array of pillar bottom coordinates.
    color : str, default="black"
        Base colour for the grid lines, pillars and arrow tips.
    line_width : float, default=2.0
        Width of the top cage lines. Everything else is derived from this.
    show_grid_lines : bool, default=True
        Whether to draw the top/base lattices.
    show_pillars : bool, default=True
        Whether to draw the pillars connecting the two lattices.
    show_arrows : bool, default=False
        Whether to cap each pillar with a cone at its base end. Useful for
        non-vertical pillars where direction matters; redundant clutter on a
        regular vertical grid, hence off by default.
    pillar_opacity : float, default=0.5
        Visual weight of the pillars relative to the cage. Applied as a
        colour blend when ``use_fade`` is True, otherwise as true alpha.
    max_pillars_per_axis : int or None, default=None
        Cap on how many pillars are drawn along each axis; ``None`` draws
        them all. When thinning, the outermost pillars are always kept so
        the silhouette stays closed.
    opacity : float, default=1.0
        Weight of the top cage lines, applied the same way as
        ``pillar_opacity``.
    lattice_mode : {"both", "cage", "full"}, default="both"
        ``"cage"`` draws grid lines only where pillars are, ``"full"`` draws
        the fine lattice only, ``"both"`` draws the cage over a faded fine
        lattice. Without thinning the cage already covers every node, so
        ``"both"`` collapses to ``"cage"``.
    base_fade : float, default=0.45
        How far the base lattice is blended toward the background relative
        to the top lattice. Cheap depth cue; set to 0 to match them.
    texture_fade : float, default=0.75
        How far the full-resolution lattice is faded when ``lattice_mode``
        is ``"both"``, so it reads as texture under the cage.
    use_fade : bool, default=True
        Blend toward the background instead of using alpha. Order-
        independent, so overlapping lines do not blotch.
    background : Any, optional
        Colour the fade blends toward, in any form ``Color`` accepts. The
        viewer passes its theme background; defaults to the current plotter
        background when called directly.
    render_lines_as_tubes : bool, default=True
        Round caps and joined corners instead of flat-capped quads, which
        otherwise notch wherever two lines cross.

    Notes
    -----
    Thin dark lines alias badly and shimmer while orbiting, and translucent
    lines (``use_fade=False``) render order-dependently. Both are fixed by
    plotter-wide settings -- ``anti_aliasing`` and ``depth_peeling`` on
    ``PyVista3DViewerTheme`` -- rather than here, because the viewer rebuilds
    the plotter for screenshots and only replays ``add_mesh`` calls.
    """
    pillar_top = np.asarray(pillar_top, dtype=np.float64)
    pillar_bottom = np.asarray(pillar_bottom, dtype=np.float64)

    if pillar_top.ndim != 3 or pillar_top.shape[2] != 3:
        raise ValueError(
            f"pillar_top must be (nj+1, ni+1, 3), got {pillar_top.shape}"
        )
    if pillar_top.shape != pillar_bottom.shape:
        raise ValueError(
            f"Shape mismatch: pillar_top {pillar_top.shape} vs "
            f"pillar_bottom {pillar_bottom.shape}"
        )
    if lattice_mode not in ("both", "cage", "full"):
        raise ValueError(
            f"lattice_mode must be 'both', 'cage' or 'full', got {lattice_mode!r}"
        )

    if pillar_top[..., 0].size == 0:
        return

    base_rgb = Color(color).as_rgb()
    bg = Color(background).as_rgb() if background is not None else _plotter_background(plotter)

    def _style(weight: float, extra_fade: float = 0.0) -> dict:
        """Turn a 0-1 visual weight into colour/opacity keyword arguments."""
        if use_fade:
            amount = (1.0 - weight) + extra_fade * weight
            return {"color": _fade(base_rgb, amount, bg), "opacity": 1.0}
        return {
            "color": _fade(base_rgb, extra_fade, bg),
            "opacity": float(min(max(weight, 0.0), 1.0)),
        }

    # Colour and opacity are derived from the weights above, so a caller
    # smuggling them through **kwargs would collide with the style dict.
    kwargs = {k: v for k, v in kwargs.items() if k not in ("color", "opacity")}

    # Lines are unlit on purpose: shading a wireframe only darkens it
    # unevenly. Set explicitly so the viewer's ``lighting`` theme default
    # (applied via setdefault in its add_mesh wrapper) does not override it.
    line_kwargs = {
        "render_lines_as_tubes": render_lines_as_tubes,
        "lighting": False,
        **kwargs,
    }

    # Pillars, their arrow caps and the cage all use this same subset, so
    # every drawn pillar lands on a drawn intersection.
    nj1, ni1 = pillar_top.shape[:2]
    if max_pillars_per_axis is None:
        jj, ii = np.arange(nj1), np.arange(ni1)
    else:
        jj = _sample_indices(nj1, max_pillars_per_axis)
        ii = _sample_indices(ni1, max_pillars_per_axis)
    sel = np.ix_(jj, ii)

    # With no thinning the cage is the full lattice; drawing the faded
    # texture underneath it would just double every line.
    thinned = len(jj) < nj1 or len(ii) < ni1
    if lattice_mode == "both" and not thinned:
        lattice_mode = "cage"

    top = pillar_top[sel]
    bot = pillar_bottom[sel]
    top_flat = top.reshape(-1, 3)
    bot_flat = bot.reshape(-1, 3)

    # ------------------------------------------------------------------
    # Lattice grid lines -- the part that makes it read as a grid
    # ------------------------------------------------------------------
    if show_grid_lines:
        lattices = (
            ("top", pillar_top, 0.0),
            ("base", pillar_bottom, base_fade),
        )

        for name, nodes, depth_fade in lattices:
            if lattice_mode in ("both", "full"):
                mesh = _lattice_lines(nodes)
                if mesh is not None:
                    fine_fade = texture_fade if lattice_mode == "both" else 0.0
                    plotter.add_mesh(
                        mesh,
                        name=f"pillars:lattice:{name}",
                        line_width=max(line_width * 0.5, 0.5),
                        **_style(opacity, min(depth_fade + fine_fade, 0.95)),
                        **line_kwargs,
                    )

            if lattice_mode in ("both", "cage"):
                mesh = _lattice_lines(nodes, jj=jj, ii=ii)
                if mesh is not None:
                    plotter.add_mesh(
                        mesh,
                        name=f"pillars:cage:{name}",
                        line_width=max(line_width * (0.75 if name == "base" else 1.0), 0.5),
                        **_style(opacity, depth_fade),
                        **line_kwargs,
                    )

    # ------------------------------------------------------------------
    # Pillars
    # ------------------------------------------------------------------
    if show_pillars:
        plotter.add_mesh(
            _segments(top_flat, bot_flat),
            name="pillars:shafts",
            line_width=max(line_width * 0.6, 0.5),
            **_style(pillar_opacity),
            **line_kwargs,
        )

    if not show_arrows:
        return

    # ------------------------------------------------------------------
    # Optional direction cones at the base end
    # ------------------------------------------------------------------
    directions = bot_flat - top_flat
    lengths = np.linalg.norm(directions, axis=1)
    keep = lengths > 0
    if not keep.any():
        return
    unit_dirs = directions[keep] / lengths[keep, np.newaxis]

    # Spacing is measured on the thinned grid, since that is what the cones
    # sit on. Measuring it on the full lattice makes them come out roughly
    # nj/max_pillars_per_axis times too small -- specks on the line ends.
    mid = 0.5 * (top + bot)
    lateral = []
    if mid.shape[1] > 1:
        lateral.append(np.linalg.norm(mid[:, 1:] - mid[:, :-1], axis=2).ravel())
    if mid.shape[0] > 1:
        lateral.append(np.linalg.norm(mid[1:, :] - mid[:-1, :], axis=2).ravel())
    spacing = np.median(np.concatenate(lateral)) if lateral else lengths[keep].mean()

    cone_len = float(min(spacing * 0.35, lengths[keep].mean() * 0.3))
    if cone_len <= 0:
        return

    tips = pv.PolyData(bot_flat[keep] - unit_dirs * cone_len * 0.5)
    tips["direction"] = unit_dirs
    cones = tips.glyph(
        orient="direction",
        scale=False,
        geom=pv.Cone(radius=cone_len * 0.35, height=cone_len, resolution=16),
    )
    plotter.add_mesh(
        cones,
        name="pillars:arrows",
        **_style(pillar_opacity),
        **kwargs,
    )