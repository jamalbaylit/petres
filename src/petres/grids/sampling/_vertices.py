import numpy as np
from ._validation import _validate_vertex_array




    
def _resolve_1d_vertices(
    *,
    values: np.ndarray | None = None,
    lim: tuple[float, float] | None = None,
    n: int | None = None,
    d: float | None = None,
    name: str = "x",
) -> np.ndarray:
    using_values = values is not None
    using_bounds = lim is not None

    if using_values and using_bounds:
        raise ValueError(
            f"Provide either explicit '{name}' values or '{name}lim', not both."
        )

    if not using_values and not using_bounds:
        raise ValueError(
            f"Provide either explicit '{name}' values or '{name}lim'."
        )

    if using_values:
        arr = _validate_vertex_array(arr, name)
        return arr

    # bounds mode
    try:
        vmin, vmax = map(float, lim)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"'{name}lim' must be a 2-item tuple like ({name}min, {name}max): {e}"
        ) from e

    if not np.isfinite(vmin) or not np.isfinite(vmax):
        raise ValueError(f"'{name}lim' values must be finite.")
    if vmax <= vmin:
        raise ValueError(f"'{name}lim' must satisfy max > min.")

    using_n = n is not None
    using_d = d is not None

    if using_n and using_d:
        raise ValueError(
            f"Provide either '{name}' cell count ('n') or spacing ('d'), not both."
        )
    if not using_n and not using_d:
        raise ValueError(
            f"When using '{name}lim', provide either '{name}' cell count ('n') or spacing ('d')."
        )

    if using_n:
        if not isinstance(n, int):
            raise TypeError(f"'{name}' cell count must be an integer.")
        if n < 1:
            raise ValueError(f"'{name}' cell count must be >= 1.")
        return np.linspace(vmin, vmax, n + 1, dtype=float)

    # spacing mode
    try:
        d = float(d)
    except (TypeError, ValueError) as e:
        raise ValueError(f"'{name}' spacing must be a float: {e}") from e

    if not np.isfinite(d):
        raise ValueError(f"'{name}' spacing must be finite.")
    if d <= 0:
        raise ValueError(f"'{name}' spacing must be > 0.")

    n_cells = max(int(np.floor((vmax - vmin) / d)), 1)
    return np.linspace(vmin, vmax, n_cells + 1, dtype=float)


def _resolve_xy_vertices(
    *,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    ni: int | None = None,
    nj: int | None = None,
    dx: float | None = None,
    dy: float | None = None,
) -> tuple[np.ndarray, np.ndarray]:

    xv = _resolve_1d_vertices(
        values=x,
        lim=xlim,
        n=ni,
        d=dx,
        name="x",
    )

    yv = _resolve_1d_vertices(
        values=y,
        lim=ylim,
        n=nj,
        d=dy,
        name="y",
    )

    return xv, yv


def _resolve_xyz_vertices(
    *,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    z: np.ndarray | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    zlim: tuple[float, float] | None = None,
    ni: int | None = None,
    nj: int | None = None,
    nk: int | None = None,
    dx: float | None = None,
    dy: float | None = None,
    dz: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:

    xv = _resolve_1d_vertices(
        values=x,
        lim=xlim,
        n=ni,
        d=dx,
        name="x",
    )

    yv = _resolve_1d_vertices(
        values=y,
        lim=ylim,
        n=nj,
        d=dy,
        name="y",
    )

    zv = _resolve_1d_vertices(
        values=z,
        lim=zlim,
        n=nk,
        d=dz,
        name="z",
    )
    return xv, yv, zv