from scipy.interpolate import CloughTocher2DInterpolator
from numpy.typing import ArrayLike, DTypeLike, NDArray
from typing import Any
import numpy as np

from ..._utils._chunking import iter_chunks
from ..base import BaseInterpolator

class CloughTocherInterpolator(BaseInterpolator):
    """Clough-Tocher 2D cubic interpolator.

    Clough-Tocher interpolation constructs a smooth, piecewise-cubic surface
    over a Delaunay triangulation of scattered 2D data points. The resulting
    interpolant is continuously differentiable (C1).

    Parameters
    ----------
    fill_value : float, default np.nan
        Value used for points outside the convex hull of the input points.

    tol : float, default 1e-6
        Absolute/relative tolerance used when estimating the gradients of the
        interpolating surface.

    maxiter : int, default 400
        Maximum number of iterations used for gradient estimation.

    rescale : bool, default False
        Rescale coordinates to a unit cube before interpolation. This can be
        useful when coordinate dimensions have very different scales.

    dtype : numpy.dtype or str, default numpy.float64
        Storage dtype for input data and outputs.

    chunk_size : int or None, default None
        Number of query points processed per batch during prediction.
        If None, all query points are processed at once.

    Notes
    -----
    Clough-Tocher interpolation is restricted to two-dimensional coordinates.
    The interpolator internally uses a Delaunay triangulation and constructs
    piecewise cubic polynomials that are C1-continuous across triangle
    boundaries.

    Examples
    --------
    >>> interp = CloughTocherInterpolator(chunk_size=10_000)
    >>> interp.fit(
    ...     [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]],
    ...     [0.0, 1.0, 1.0],
    ... )
    >>> interp.predict([[0.25, 0.25]])
    array([0.5])
    """

    allowed_dims = (2,)

    def __init__(
        self,
        *,
        fill_value: float = np.nan,
        tol: float = 1e-6,
        maxiter: int = 400,
        rescale: bool = False,
        dtype: DTypeLike = np.float64,
        chunk_size: int | None = None,
    ) -> None:
        """Initialize the Clough-Tocher interpolator.

        Raises
        ------
        ValueError
            If ``tol <= 0``, ``maxiter <= 0``, or ``chunk_size <= 0``.
        """
        super().__init__(dtype=dtype)

        if tol <= 0:
            raise ValueError(f"`tol` must be > 0. Got {tol}.")

        if maxiter <= 0:
            raise ValueError(f"`maxiter` must be > 0. Got {maxiter}.")

        if chunk_size is not None and chunk_size <= 0:
            raise ValueError(
                f"`chunk_size` must be > 0. Got {chunk_size}."
            )

        self.fill_value = self.dtype.type(fill_value)
        self.tol = float(tol)
        self.maxiter = int(maxiter)
        self.rescale = bool(rescale)
        self.chunk_size = int(chunk_size) if chunk_size is not None else None

        # Fitted SciPy interpolator.
        self._interpolator: CloughTocher2DInterpolator | None = None

    def _fit_impl(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> None:
        """Construct the Clough-Tocher interpolant."""

        if coordinates.shape[0] < 3:
            raise ValueError(
                "Clough-Tocher interpolation requires at least 3 sample points. "
                f"Got {coordinates.shape[0]}."
            )

        self._interpolator = CloughTocher2DInterpolator(
            coordinates,
            values,
            fill_value=self.fill_value,
            tol=self.tol,
            maxiter=self.maxiter,
            rescale=self.rescale,
        )

    def _predict_impl(
        self,
        coordinates: NDArray[Any],
    ) -> NDArray[Any]:
        """Evaluate the interpolant in chunks."""

        interpolator = self._interpolator
        assert interpolator is not None

        out = np.empty(coordinates.shape[0], dtype=self.dtype)

        for slc, coordinates_chunk in iter_chunks(
            coordinates,
            self.chunk_size,
        ):
            out[slc] = np.asarray(
                interpolator(coordinates_chunk),
                dtype=self.dtype,
            )

        return out