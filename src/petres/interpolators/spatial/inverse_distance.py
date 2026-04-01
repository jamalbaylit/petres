from __future__ import annotations
from typing import Literal
import numpy as np

from ..base import BaseInterpolator



class InverseDistanceWeightingInterpolator(BaseInterpolator):
    """Inverse Distance Weighting (IDW) interpolator.

    Parameters
    ----------
    power : float, default 2.0
        Weight exponent p. Larger values make the interpolation more local.
        Common values: 1.0–3.0.
    eps : float, default 1e-12
        Small value to avoid division-by-zero and stabilize near-zero distances.
    neighbors : int or None, optional
        If provided, use only the k nearest samples per query; otherwise use
        all samples.
    mode : {'average', 'sum'}, default 'average'
        Weighting mode. ``'average'`` computes normalized weighted averages;
        ``'sum'`` returns the weighted sum (rarely used).
    dtype : numpy.dtype or str, default numpy.float64
        Storage dtype for cached arrays and outputs.
    """

    def __init__(
        self,
        power: float = 2.0,
        eps: float = 1e-12,
        neighbors: int | None = None,
        mode: Literal["average", "sum"] = "average",
        dtype: np.dtype | str = np.float64,
    ) -> None:
        """Initialize an inverse-distance weighting interpolator.

        Parameters
        ----------
        power : float, default=2.0
            Weight exponent used in $w = 1 / d^p$. Larger values emphasize
            nearby samples more strongly.
        eps : float, default=1e-12
            Positive numerical guard added to distances before exponentiation.
            It stabilizes weight computation near zero distances.
        neighbors : int or None, default=None
            Number of nearest neighbors to use per prediction point. If
            ``None``, all fitted samples are used.
        mode : {'average', 'sum'}, default='average'
            Aggregation mode for weighted values.
            ``'average'`` returns normalized weighted averages;
            ``'sum'`` returns unnormalized weighted sums.
        dtype : numpy.dtype or str, default=numpy.float64
            Target NumPy dtype used for cached arrays and prediction outputs.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If ``power <= 0``, ``eps <= 0``, ``neighbors`` is not positive
            when provided, or ``mode`` is not one of ``'average'`` or
            ``'sum'``.

        Notes
        -----
        When an exact coordinate match is found during prediction, the
        interpolator returns the matching sample value directly (or the mean of
        duplicate exact matches), independent of ``mode``.

        Examples
        --------
        >>> interp = InverseDistanceWeightingInterpolator(power=2.0, neighbors=8)
        >>> interp.fit([[0.0, 0.0], [1.0, 1.0]], [10.0, 20.0])
        >>> interp.predict([[0.5, 0.5]]).shape
        (1,)
        """
        super().__init__()

        if power <= 0:
            raise ValueError(f"`power` must be > 0. Got {power}.")
        if eps <= 0:
            raise ValueError(f"`eps` must be > 0. Got {eps}.")
        if neighbors is not None and neighbors <= 0:
            raise ValueError(f"`neighbors` must be a positive int or None. Got {neighbors}.")
        if mode not in ("average", "sum"):
            raise ValueError(f"`mode` must be 'average' or 'sum'. Got {mode!r}.")

        self.power = float(power)
        self.eps = float(eps)
        self.neighbors = int(neighbors) if neighbors is not None else None
        self.mode: Literal["average", "sum"] = mode
        self.dtype = np.dtype(dtype)

        # fitted state
        self._X: np.ndarray | None = None  # (n, dim)
        self._y: np.ndarray | None = None  # (n,)

    def _fit_impl(self, coordinates: np.ndarray, values: np.ndarray) -> None:
        """Store validated training coordinates and values.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, dim)``.
        values : numpy.ndarray
            Training values with shape ``(n_samples,)``.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If array shapes are invalid, sample counts differ, arrays are
            empty, non-finite values are present, or ``neighbors`` exceeds the
            number of fitted samples.
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

        if not np.isfinite(X).all():
            raise ValueError("`coordinates` contains NaN/Inf.")
        if not np.isfinite(y).all():
            raise ValueError("`values` contains NaN/Inf.")

        self._X = X
        self._y = y
        self._is_fitted = True

    def _predict_impl(self, coordinates: np.ndarray) -> np.ndarray:
        """Predict values for query coordinates using IDW weighting.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_points,)`` and dtype configured by
            ``dtype``.

        Raises
        ------
        ValueError
            If ``coordinates`` is not 2D, has a dimensionality mismatch with
            fitted data, or contains non-finite values.
        RuntimeError
            If prediction is requested before fitting.
        """
        self._check_fitted()
        assert self._X is not None and self._y is not None

        Q = np.asarray(coordinates, dtype=self.dtype)
        if Q.ndim != 2:
            raise ValueError(f"`coordinates` must be 2D of shape (n_points, dim). Got shape {Q.shape}.")
        if Q.shape[1] != self._X.shape[1]:
            raise ValueError(
                f"Dim mismatch: query dim={Q.shape[1]} but fitted dim={self._X.shape[1]}."
            )
        if Q.shape[0] == 0:
            return np.asarray([], dtype=self.dtype)

        if not np.isfinite(Q).all():
            raise ValueError("Query `coordinates` contains NaN/Inf.")

        # Compute squared distances: (m, n)
        # Using (a-b)^2 = a^2 + b^2 - 2ab for efficiency.
        X = self._X
        y = self._y

        Q2 = np.sum(Q * Q, axis=1, keepdims=True)          # (m, 1)
        X2 = np.sum(X * X, axis=1, keepdims=True).T        # (1, n)
        d2 = Q2 + X2 - 2.0 * (Q @ X.T)                     # (m, n)
        d2 = np.maximum(d2, 0.0)                           # numeric guard
        d = np.sqrt(d2, dtype=self.dtype)

        # Exact-match handling: if any distance is ~0, return that sample's value.
        # (No need to compute weights for those rows.)
        zero_mask = d <= self.eps  # (m, n)
        has_exact = zero_mask.any(axis=1)  # (m,)

        out = np.empty(Q.shape[0], dtype=self.dtype)

        # Rows with exact matches
        if np.any(has_exact):
            rows = np.where(has_exact)[0]
            # If multiple exact matches (duplicate coordinates), average their values
            for i in rows:
                out[i] = y[zero_mask[i]].mean(dtype=self.dtype)

        # Rows without exact matches
        rows = np.where(~has_exact)[0]
        if rows.size == 0:
            return out

        d_sub = d[rows]  # (m2, n)

        if self.neighbors is None:
            # Weights: w = 1 / (d^p)
            w = 1.0 / np.power(d_sub + self.eps, self.power, dtype=self.dtype)  # (m2, n)
            if self.mode == "sum":
                out[rows] = w @ y
            else:
                denom = np.sum(w, axis=1)
                out[rows] = (w @ y) / denom
            return out

        # KNN IDW: select k nearest for each query row
        k = self.neighbors
        # argpartition gets k smallest distances per row (unordered)
        idx = np.argpartition(d_sub, kth=k - 1, axis=1)[:, :k]  # (m2, k)

        # gather distances and values
        d_knn = np.take_along_axis(d_sub, idx, axis=1)          # (m2, k)
        y_knn = y[idx]                                          # (m2, k)

        w = 1.0 / np.power(d_knn + self.eps, self.power, dtype=self.dtype)  # (m2, k)

        if self.mode == "sum":
            out[rows] = np.sum(w * y_knn, axis=1)
        else:
            out[rows] = np.sum(w * y_knn, axis=1) / np.sum(w, axis=1)

        return out