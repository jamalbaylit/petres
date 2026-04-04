import numpy as np
import pyvista as pv
from ....._utils._color import Color

def _add_pillars(
    backend,
    pillar_top: np.ndarray,
    pillar_bottom: np.ndarray,
    shaft_color: str = "red",
    shaft_radius_factor: float = 0.08,
    tip_radius_factor: float = 2.5,
    tip_length_factor: float = 0.12,
    opacity: float = 1.0,
    **kwargs
) -> None:
    """
    Add arrow lines (pillars) from top points to bottom points, similar to
    Petrel's pillar visualisation.  Adapts visually to any XYZ scale or
    aspect ratio by deriving sizes from the structured grid spacing.

    Parameters
    ----------
    plotter : pv.Plotter
        The PyVista plotter to add the pillars to.
    pillar_top : np.ndarray
        (nj+1, ni+1, 3) array of pillar top coordinates.
    pillar_bottom : np.ndarray
        (nj+1, ni+1, 3) array of pillar bottom coordinates.
    shaft_color : str
        Color of the shaft tubes.
    tip_color : str
        Color of the arrowhead cones.
    shaft_radius_factor : float
        Shaft radius as a fraction of the median lateral pillar spacing.
    tip_radius_factor : float
        Cone base radius as a multiple of the shaft radius.
    tip_length_factor : float
        Cone length as a fraction of each individual pillar length.
    opacity : float
        Opacity for both shaft and tip actors.
    """
    plotter = backend.plotter
    shaft_color = Color(shaft_color).as_rgb()

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

    nj1, ni1, _ = pillar_top.shape

    # ------------------------------------------------------------------
    # Compute adaptive sizes from the STRUCTURED grid spacing
    # ------------------------------------------------------------------
    # Use pillar midpoints so sizing reflects actual pillar positions
    mid = 0.5 * (pillar_top + pillar_bottom)  # (nj+1, ni+1, 3)

    lateral_dists = []
    if ni1 > 1:
        # i-direction neighbor distances
        di = np.linalg.norm(mid[:, 1:, :] - mid[:, :-1, :], axis=2)  # (nj+1, ni)
        lateral_dists.append(di.ravel())
    if nj1 > 1:
        # j-direction neighbor distances
        dj = np.linalg.norm(mid[1:, :, :] - mid[:-1, :, :], axis=2)  # (nj, ni+1)
        lateral_dists.append(dj.ravel())

    if lateral_dists:
        median_spacing = np.median(np.concatenate(lateral_dists))
    else:
        # Single pillar fallback — use pillar length
        median_spacing = np.linalg.norm(
            pillar_bottom.ravel() - pillar_top.ravel()
        )

    shaft_radius = max(median_spacing * shaft_radius_factor, 1e-6)
    cone_radius = shaft_radius * tip_radius_factor

    # ------------------------------------------------------------------
    # Flatten to (N, 3)
    # ------------------------------------------------------------------
    top = pillar_top.reshape(-1, 3)
    bot = pillar_bottom.reshape(-1, 3)
    n = top.shape[0]
    if n == 0:
        return

    directions = bot - top                                       # (N, 3)
    lengths = np.linalg.norm(directions, axis=1, keepdims=True)  # (N, 1)
    safe_lengths = np.where(lengths > 0, lengths, 1.0)
    unit_dirs = directions / safe_lengths                        # (N, 3)

    # Per-pillar cone length — also capped by an absolute limit relative
    # to the lateral spacing so cones stay proportional in stretched scenes
    max_cone_abs = median_spacing * 1.5
    cone_lengths = np.minimum(
        np.clip(lengths.ravel() * tip_length_factor, 0.0, lengths.ravel() * 0.4),
        max_cone_abs,
    )                                                            # (N,)

    shaft_bottoms = bot - unit_dirs * cone_lengths[:, np.newaxis]

    # ------------------------------------------------------------------
    # Shaft tubes
    # ------------------------------------------------------------------
    shaft_pts = np.empty((2 * n, 3), dtype=np.float64)
    shaft_pts[0::2] = top
    shaft_pts[1::2] = shaft_bottoms

    cell_conn = np.empty((n, 3), dtype=np.int64)
    cell_conn[:, 0] = 2
    cell_conn[:, 1] = np.arange(0, 2 * n, 2)
    cell_conn[:, 2] = np.arange(1, 2 * n, 2)

    shaft_lines = pv.PolyData(shaft_pts, lines=cell_conn.ravel())
    shaft_tubes = shaft_lines.tube(radius=shaft_radius, n_sides=12)

    plotter.add_mesh(
        shaft_tubes,
        color=shaft_color,
        opacity=opacity,
        smooth_shading=True,
    )


