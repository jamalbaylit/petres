from __future__ import annotations

from typing import Any
from typing import Literal
import numpy as np
from numpy.typing import DTypeLike, NDArray
from scipy.interpolate import RBFInterpolator

from ..base import BaseInterpolator


class RadialBasisFunctionInterpolator(BaseInterpolator):
    """Interpolate scalar values with SciPy radial basis functions.

    This interpolator wraps :class:`scipy.interpolate.RBFInterpolator` and
    validates input shapes and hyperparameters before fitting.

    Parameters
    ----------
    kernel : {'linear', 'thin_plate_spline', 'cubic', 'quintic', 'multiquadric', 'inverse_multiquadric', 'inverse_quadratic', 'gaussian'}, default 'thin_plate_spline'
        Radial kernel passed to ``scipy.interpolate.RBFInterpolator``.
    epsilon : float or None, optional
        Shape parameter for some kernels. Must be > 0 when provided.
    smoothing : float, default 0.0
        Non-negative smoothing factor. ``0.0`` yields exact interpolation.
    neighbors : int or None, optional
        If provided, use only the k nearest samples per query; must be > 0.
    degree : int or None, optional
        Degree of appended polynomial term. ``None`` uses SciPy defaults.
    dtype : numpy.typing.DTypeLike, default numpy.float64
        Storage dtype for cached arrays and outputs.

    Notes
    -----
    The implementation expects scalar targets with shape ``(n_samples,)``.
    """

    def __init__(
        self,
        kernel: Literal[
            "linear",
            "thin_plate_spline",
            "cubic",
            "quintic",
            "multiquadric",
            "inverse_multiquadric",
            "inverse_quadratic",
            "gaussian",
        ] = "thin_plate_spline",
        epsilon: float | None = None,
        smoothing: float = 0.0,
        neighbors: int | None = None,
        degree: int | None = None,
        dtype: DTypeLike = np.float64,
    ) -> None:
        """Initialize interpolation hyperparameters.

        Raises
        ------
        ValueError
            If ``epsilon`` is not positive, ``smoothing`` is negative,
            ``neighbors`` is non-positive, or ``degree`` is negative.
        """
        super().__init__()

        if epsilon is not None and epsilon <= 0:
            raise ValueError(f"`epsilon` must be > 0 when provided. Got {epsilon}.")
        if smoothing < 0:
            raise ValueError(f"`smoothing` must be >= 0. Got {smoothing}.")
        if neighbors is not None and neighbors <= 0:
            raise ValueError(f"`neighbors` must be a positive int or None. Got {neighbors}.")
        if degree is not None and degree < 0:
            raise ValueError(f"`degree` must be >= 0 or None. Got {degree}.")

        self.kernel = kernel
        self.epsilon = float(epsilon) if epsilon is not None else None
        self.smoothing = float(smoothing)
        self.neighbors = int(neighbors) if neighbors is not None else None
        self.degree = int(degree) if degree is not None else None
        self.dtype = np.dtype(dtype)

        self._rbf: RBFInterpolator | None = None

    def _fit_impl(self, coordinates: NDArray[np.float64], values: NDArray[np.float64]) -> None:
        """Fit the underlying RBF interpolator from validated arrays.

        Parameters
        ----------
        coordinates : numpy.typing.NDArray[numpy.float64]
            Training coordinates with shape ``(n_samples, dim)``.
        values : numpy.typing.NDArray[numpy.float64]
            Scalar training targets with shape ``(n_samples,)``.
        """
        X = np.asarray(coordinates, dtype=self.dtype)
        y = np.asarray(values, dtype=self.dtype)

        if X.ndim != 2:
            raise ValueError(f"`coordinates` must be 2D of shape (n_samples, dim). Got shape {X.shape}.")
        if y.ndim != 1:
            raise ValueError(f"`values` must be 1D of shape (n_samples,). Got shape {y.shape}.")
        if X.shape[0] != y.shape[0]:
            raise ValueError(
                f"Number of samples mismatch: coordinates has {X.shape[0]}, values has {y.shape[0]}."
            )
        if X.shape[0] == 0:
            raise ValueError("Cannot fit with zero samples.")

        if self.neighbors is not None and self.neighbors > X.shape[0]:
            raise ValueError(
                f"`neighbors`={self.neighbors} cannot be greater than n_samples={X.shape[0]}."
            )

        kwargs: dict[str, object] = {
            "kernel": self.kernel,
            "smoothing": self.smoothing,
            "neighbors": self.neighbors,
            "degree": self.degree,
        }
        if self.epsilon is not None:
            kwargs["epsilon"] = self.epsilon

        try:
            self._rbf = RBFInterpolator(X, y, **kwargs)
        except Exception as exc:
            raise ValueError(f"Failed to construct RBF interpolator: {exc}") from exc

        self._is_fitted = True

    def _predict_impl(self, coordinates: NDArray[np.float64]) -> NDArray[np.float64]:
        """Predict interpolated values at query coordinates.

        Parameters
        ----------
        coordinates : numpy.typing.NDArray[numpy.float64]
            Query coordinates with shape ``(n_points, dim)``.

        Returns
        -------
        numpy.typing.NDArray[numpy.float64]
            Interpolated values with shape ``(n_points,)`` and configured
            ``dtype``.
        """
        self._check_fitted()
        assert self._rbf is not None

        Q = np.asarray(coordinates, dtype=self.dtype)

        if Q.ndim != 2:
            raise ValueError(f"`coordinates` must be 2D of shape (n_points, dim). Got shape {Q.shape}.")

        if Q.shape[0] == 0:
            return np.asarray([], dtype=self.dtype)

        values = self._rbf(Q)
        return np.asarray(values, dtype=self.dtype)