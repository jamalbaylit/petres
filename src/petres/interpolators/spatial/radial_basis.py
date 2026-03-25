from __future__ import annotations

from typing import Literal
import numpy as np
from scipy.interpolate import RBFInterpolator

from ..base import BaseInterpolator


class RadialBasisFunctionInterpolator(BaseInterpolator):
    """
    Radial Basis Function (RBF) interpolator.

    Parameters
    ----------
    kernel:
        Radial kernel function used by SciPy's ``RBFInterpolator``.
    epsilon:
        Shape parameter for certain kernels. Must be > 0 when provided.
        If None, SciPy selects its default behavior.
    smoothing:
        Non-negative smoothing factor. ``0.0`` gives exact interpolation.
    neighbors:
        If provided, uses only the k nearest sample points per query point.
        Must be a positive integer.
    degree:
        Degree of the added polynomial term. If None, SciPy selects defaults.
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
        dtype: np.dtype | str = np.float64,
    ):
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

    def _fit_impl(self, coordinates: np.ndarray, values: np.ndarray) -> None:
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

    def _predict_impl(self, coordinates: np.ndarray) -> np.ndarray:
        self._check_fitted()
        assert self._rbf is not None

        Q = np.asarray(coordinates, dtype=self.dtype)

        if Q.ndim != 2:
            raise ValueError(f"`coordinates` must be 2D of shape (n_points, dim). Got shape {Q.shape}.")

        if Q.shape[0] == 0:
            return np.asarray([], dtype=self.dtype)

        values = self._rbf(Q)
        return np.asarray(values, dtype=self.dtype)