from __future__ import annotations

import numpy as np

def _resolve_xy_sampling(
    *,
    x: np.ndarray | None = None,
    y: np.ndarray | None = None,
    xlim: tuple[float, float] | None = None,
    ylim: tuple[float, float] | None = None,
    nx: int | None = None,
    ny: int | None = None,
    dx: float | None = None,
    dy: float | None = None,
    default_nx: int = 200,
    default_ny: int = 200,
) -> tuple[np.ndarray, np.ndarray]:
    """
        Resolve 2D sampling coordinates (x, y) for surface or volume evaluation.

        This function supports two mutually exclusive sampling modes:

        1) Explicit axes mode
        Provide `x` and `y` as 1D coordinate arrays.

        2) Bounds-based mode
        Provide spatial bounds (`xlim`, `ylim`) together with either:
            - number of samples (`nx`, `ny`), or
            - spacing (`dx`, `dy`).

        Parameters
        ----------
        x : ndarray of shape (nx,), optional
            Explicit 1D array of x-coordinates.
            Must be provided together with `y`.
            Cannot be used together with `xlim`/`ylim`.

        y : ndarray of shape (ny,), optional
            Explicit 1D array of y-coordinates.
            Must be provided together with `x`.
            Cannot be used together with `xlim`/`ylim`.

        xlim : tuple of float (xmin, xmax), optional
            Spatial bounds in x-direction. Must satisfy xmax > xmin.
            Required when using bounds-based mode.

        ylim : tuple of float (ymin, ymax), optional
            Spatial bounds in y-direction. Must satisfy ymax > ymin.
            Required when using bounds-based mode.

        nx : int, optional
            Number of sampling points in x-direction when using bounds mode.
            Must be >= 2. Cannot be used together with `dx`.

        ny : int, optional
            Number of sampling points in y-direction when using bounds mode.
            Must be >= 2. Cannot be used together with `dy`.

        dx : float, optional
            Grid spacing in x-direction when using bounds mode.
            Must be > 0. Cannot be used together with `nx`.

        dy : float, optional
            Grid spacing in y-direction when using bounds mode.
            Must be > 0. Cannot be used together with `ny`.

        default_nx : int, default=200
            Default number of x samples when bounds are provided and neither
            `nx` nor `dx` are specified.

        default_ny : int, default=200
            Default number of y samples when bounds are provided and neither
            `ny` nor `dy` are specified.

        Returns
        -------
        x : ndarray of shape (nx,)
            Resolved 1D x-coordinate array.

        y : ndarray of shape (ny,)
            Resolved 1D y-coordinate array.

        Raises
        ------
        ValueError
            If:
            - Both explicit axes and bounds-based parameters are provided.
            - Only one of `x` or `y` is given.
            - Only one of `xlim` or `ylim` is given.
            - Both (nx/ny) and (dx/dy) are provided.
            - Invalid bounds (xmax <= xmin or ymax <= ymin).
            - Invalid resolution parameters (nx < 2, ny < 2, dx <= 0, dy <= 0).

        Notes
        -----
        Exactly one sampling mode must be selected:

        • Explicit axes mode:
            Provide `x` and `y`.

        • Bounds mode:
            Provide `xlim` and `ylim`, and optionally:
                - `nx`, `ny`  → uniform sampling using number of points
                - `dx`, `dy`  → uniform sampling using spacing

        In bounds mode, endpoints are included in the generated arrays.

        Examples
        --------
        Explicit axes:

        >>> x = np.linspace(0, 5000, 200)
        >>> y = np.linspace(0, 3000, 120)
        >>> x_res, y_res = _resolve_xy_sampling(x=x, y=y)

        Bounds + number of samples:

        >>> x_res, y_res = _resolve_xy_sampling(
        ...     xlim=(0, 5000),
        ...     ylim=(0, 3000),
        ...     nx=200,
        ...     ny=120,
        ... )

        Bounds + spacing:

        >>> x_res, y_res = _resolve_xy_sampling(
        ...     xlim=(0, 5000),
        ...     ylim=(0, 3000),
        ...     dx=25.0,
        ...     dy=25.0,
        ... )
    """
        
    using_axes = (x is not None) or (y is not None)
    using_bounds = (xlim is not None) or (ylim is not None)

    if using_axes and using_bounds:
        raise ValueError("Provide either (x, y) OR (xlim, ylim), not both.")

    if using_axes:
        if x is None or y is None:
            raise ValueError("If using axes sampling, both x and y must be provided.")
        x = np.asarray(x, dtype=float).ravel()
        y = np.asarray(y, dtype=float).ravel()
        if x.ndim != 1 or y.ndim != 1:
            raise ValueError("x and y must be 1D arrays.")
        if x.size < 2 or y.size < 2:
            raise ValueError("x and y must each contain at least 2 points.")
        return x, y

    # Bounds mode
    if xlim is None or ylim is None:
        raise ValueError("If using bounds sampling, both xlim and ylim must be provided.")

    xmin, xmax = map(float, xlim)
    ymin, ymax = map(float, ylim)
    if not (xmax > xmin and ymax > ymin):
        raise ValueError("Invalid bounds: require xmax>xmin and ymax>ymin.")

    using_n = (nx is not None) or (ny is not None)
    using_d = (dx is not None) or (dy is not None)
    if using_n and using_d:
        raise ValueError("Provide either (nx, ny) OR (dx, dy), not both.")

    if using_d:
        if dx is None or dy is None:
            raise ValueError("If using spacing, both dx and dy must be provided.")
        dx = float(dx)
        dy = float(dy)
        if dx <= 0 or dy <= 0:
            raise ValueError("dx and dy must be > 0.")
        # include endpoints
        nx_ = int(np.floor((xmax - xmin) / dx)) + 1
        ny_ = int(np.floor((ymax - ymin) / dy)) + 1
        nx_ = max(nx_, 2)
        ny_ = max(ny_, 2)
        x = np.linspace(xmin, xmax, nx_, dtype=float)
        y = np.linspace(ymin, ymax, ny_, dtype=float)
        return x, y

    # nx/ny mode (with defaults)
    nx_ = int(nx) if nx is not None else default_nx
    ny_ = int(ny) if ny is not None else default_ny
    if nx_ < 2 or ny_ < 2:
        raise ValueError("nx and ny must be >= 2.")
    x = np.linspace(xmin, xmax, nx_, dtype=float)
    y = np.linspace(ymin, ymax, ny_, dtype=float)
    return x, y