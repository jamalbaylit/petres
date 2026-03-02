from __future__ import annotations

import numpy as np

def _resolve_xy_sampling(
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
    """
        Resolve 2D sampling coordinates (x, y) for surface or volume evaluation.

        This function supports two mutually exclusive sampling modes:

        1) Explicit axes mode
        Provide `x` and `y` as 1D coordinate arrays.

        2) Bounds-based mode
        Provide spatial bounds (`xlim`, `ylim`) together with either:
            - number of samples (`ni`, `nj`), or
            - spacing (`dx`, `dy`).

        Parameters
        ----------
        x : ndarray of shape (ni,), optional
            Explicit 1D array of x-coordinates.
            Must be provided together with `y`.
            Cannot be used together with `xlim`/`ylim`.

        y : ndarray of shape (nj,), optional
            Explicit 1D array of y-coordinates.
            Must be provided together with `x`.
            Cannot be used together with `xlim`/`ylim`.

        xlim : tuple of float (xmin, xmax), optional
            Spatial bounds in x-direction. Must satisfy xmax > xmin.
            Required when using bounds-based mode.

        ylim : tuple of float (ymin, ymax), optional
            Spatial bounds in y-direction. Must satisfy ymax > ymin.
            Required when using bounds-based mode.

        ni : int, optional
            Number of sampling points in x-direction when using bounds mode.
            Must be >= 2. Cannot be used together with `dx`.

        nj : int, optional
            Number of sampling points in y-direction when using bounds mode.
            Must be >= 2. Cannot be used together with `dy`.

        dx : float, optional
            Grid spacing in x-direction when using bounds mode.
            Must be > 0. Cannot be used together with `ni`.

        dy : float, optional
            Grid spacing in y-direction when using bounds mode.
            Must be > 0. Cannot be used together with `nj`.

        Returns
        -------
        x : ndarray of shape (ni,)
            Resolved 1D x-coordinate array.

        y : ndarray of shape (nj,)
            Resolved 1D y-coordinate array.

        Raises
        ------
        ValueError
            If:
            - Both explicit axes and bounds-based parameters are provided.
            - Only one of `x` or `y` is given.
            - Only one of `xlim` or `ylim` is given.
            - Both (ni/nj) and (dx/dy) are provided.
            - Invalid bounds (xmax <= xmin or ymax <= ymin).
            - Invalid resolution parameters (ni < 2, nj < 2, dx <= 0, dy <= 0).

        Notes
        -----
        Exactly one sampling mode must be selected:

        • Explicit axes mode:
            Provide `x` and `y`.

        • Bounds mode:
            Provide `xlim` and `ylim`, and optionally:
                - `ni`, `nj`  → uniform sampling using number of points
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
        ...     ni=200,
        ...     nj=120,
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

    using_n = (ni is not None) or (nj is not None)
    using_d = (dx is not None) or (dy is not None)
    if using_n and using_d:
        raise ValueError("Provide either (ni, nj) OR (dx, dy), not both.")

    if using_d:
        if dx is None or dy is None:
            raise ValueError("If using spacing, both dx and dy must be provided.")
        dx = float(dx)
        dy = float(dy)
        if dx <= 0 or dy <= 0:
            raise ValueError("dx and dy must be > 0.")
        # include endpoints
        ni_ = int(np.floor((xmax - xmin) / dx)) + 1
        nj_ = int(np.floor((ymax - ymin) / dy)) + 1
        ni_ = max(ni_, 2)
        nj_ = max(nj_, 2)
        x = np.linspace(xmin, xmax, ni_, dtype=float)
        y = np.linspace(ymin, ymax, nj_, dtype=float)
        return x, y

    # ni/nj mode (with defaults)
    assert isinstance(ni, int) and isinstance(nj, int)
    
    if ni < 1 or nj < 1:
        raise ValueError("ni and nj must be >= 1.")
    x = np.linspace(xmin, xmax, ni+1 , dtype=float)
    y = np.linspace(ymin, ymax, nj+1, dtype=float)
    return x, y