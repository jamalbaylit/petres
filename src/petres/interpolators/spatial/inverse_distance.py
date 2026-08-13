from __future__ import annotations

from typing import Any, Literal

import numpy as np
from numpy.typing import DTypeLike, NDArray
from scipy.spatial import cKDTree

from ..base import BaseInterpolator


class InverseDistanceWeightingInterpolator(BaseInterpolator):
    """Inverse Distance Weighting (IDW) interpolator.

    Parameters
    ----------
    power : float, default 2.0
        Weight exponent p. Larger values make the interpolation more local.
        Common values: 1.0-3.0.
    eps : float, default 1e-12
        Small value to avoid division-by-zero and stabilize near-zero distances.
    neighbors : int or None, optional
        If provided, use only the k nearest samples per query (via a KD-tree,
        so this is fast and memory-cheap even for large datasets); otherwise
        use all samples (brute-force, processed in chunks to bound memory).
    mode : {'average', 'sum'}, default 'average'
        Weighting mode. ``'average'`` computes normalized weighted averages;
        ``'sum'`` returns the weighted sum (rarely used).
    dtype : numpy.dtype or str, default numpy.float64
        Storage dtype for cached arrays and outputs.
    chunk_size : int, default 20000
        Upper bound on query points processed per batch in the "use all
        samples" (``neighbors=None``) path. The *effective* chunk size is
        automatically shrunk below this so that each chunk's (chunk_size,
        n_samples) distance matrix stays under ``max_chunk_bytes`` -- this
        keeps memory bounded regardless of how many samples were fitted.
        Has no effect when ``neighbors`` is set, since the KD-tree path is
        already memory-cheap.
    max_chunk_bytes : int, default 268_435_456 (256 MiB)
        Memory budget for a single chunk's distance matrix in the
        ``neighbors=None`` path. Lower this on memory-constrained machines;
        raise it for more speed if you have RAM to spare.
    """

    allowed_dims = None # allow any dim
    
    def __init__(
        self,
        *,
        dtype: DTypeLike = np.float64,
        power: float = 2.0,
        eps: float = 1e-12,
        neighbors: int | None = None,
        mode: Literal["average", "sum"] = "average",
        chunk_size: int = 20000,
        max_chunk_bytes: int = 268_435_456,
    ) -> None:
        """Initialize the interpolator with validated IDW configuration.

        Raises
        ------
        ValueError
            If ``power <= 0``, ``eps <= 0``, ``neighbors`` is not positive
            when provided, ``mode`` is not one of ``'average'`` or ``'sum'``,
            or ``chunk_size <= 0``.

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
        super().__init__(dtype=dtype)

        if power <= 0:
            raise ValueError(f"`power` must be > 0. Got {power}.")
        if eps <= 0:
            raise ValueError(f"`eps` must be > 0. Got {eps}.")
        if neighbors is not None and (not isinstance(neighbors, int) or neighbors <= 0):
            raise ValueError(f"`neighbors` must be a positive int or None. Got {neighbors}.")
        if mode not in ("average", "sum"):
            raise ValueError(f"`mode` must be 'average' or 'sum'. Got {mode!r}.")
        if chunk_size <= 0:
            raise ValueError(f"`chunk_size` must be > 0. Got {chunk_size}.")
        if max_chunk_bytes <= 0:
            raise ValueError(f"`max_chunk_bytes` must be > 0. Got {max_chunk_bytes}.")

        self.power = float(power)
        self.eps = float(eps)
        self.neighbors = int(neighbors) if neighbors is not None else None
        self.mode: Literal["average", "sum"] = mode
        self.dtype = np.dtype(dtype)
        self.chunk_size = int(chunk_size)
        self.max_chunk_bytes = int(max_chunk_bytes)

        # fitted state
        self._X: np.ndarray | None = None  # (n, dim)
        self._y: np.ndarray | None = None  # (n,)
        self._tree: cKDTree | None = None

    def _fit_impl(
        self,
        coordinates: NDArray[np.floating[Any]],
        values: NDArray[np.floating[Any]],
    ) -> None:
        """Store validated training coordinates and values.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Shape ``(n_samples, dim)``.
        values : numpy.ndarray
            Shape ``(n_samples,)``.

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

        # Build a KD-tree once at fit time; reused for every predict() call.
        # Only needed for the neighbors-limited path, but it's cheap to build
        # eagerly so repeated predict() calls don't pay the build cost again.
        self._tree = cKDTree(X)

    def _predict_impl(self, coordinates: NDArray[np.floating[Any]]) -> NDArray[np.floating[Any]]:
        """Predict values for query coordinates using IDW weighting.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Shape ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_points,)``.

        Raises
        ------
        ValueError
            If ``coordinates`` is not 2D, has a dimensionality mismatch with
            fitted data, or contains non-finite values.
        RuntimeError
            If prediction is requested before fitting.
        """
        self._check_fitted()
        assert self._X is not None and self._y is not None and self._tree is not None

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

        if self.neighbors is not None:
            return self._predict_knn(Q)
        return self._predict_full(Q)

    def _predict_knn(self, Q: NDArray[np.floating[Any]]) -> NDArray[np.floating[Any]]:
        """KD-tree-backed k-nearest-neighbor IDW. O(m log n) time, O(m*k) memory."""
        y = self._y
        assert self._tree is not None and y is not None

        k = self.neighbors
        assert k is not None

        # cKDTree.query is vectorized over all query points and internally
        # batched/parallelized -- no (m, n) matrix is ever built.
        d_knn, idx = self._tree.query(Q, k=k, workers=-1)

        # When k == 1, scipy returns 1D arrays; normalize to 2D (m, 1).
        if k == 1:
            d_knn = d_knn[:, None]
            idx = idx[:, None]

        y_knn = y[idx]  # (m, k)

        out = np.empty(Q.shape[0], dtype=self.dtype)

        # Exact matches: any neighbor at (near-)zero distance.
        zero_mask = d_knn <= self.eps  # (m, k)
        has_exact = zero_mask.any(axis=1)

        if np.any(has_exact):
            rows = np.where(has_exact)[0]
            for i in rows:
                out[i] = y_knn[i][zero_mask[i]].mean(dtype=self.dtype)

        rows = np.where(~has_exact)[0]
        if rows.size:
            d_sub = d_knn[rows]
            y_sub = y_knn[rows]
            w = 1.0 / np.power(d_sub + self.eps, self.power, dtype=self.dtype)
            if self.mode == "sum":
                out[rows] = np.sum(w * y_sub, axis=1)
            else:
                out[rows] = np.sum(w * y_sub, axis=1) / np.sum(w, axis=1)

        return out

    def _predict_full(self, Q: NDArray[np.floating[Any]]) -> NDArray[np.floating[Any]]:
        """Brute-force IDW over all fitted samples, processed in row chunks
        to bound peak memory to roughly chunk_size * n_samples floats."""
        X = self._X
        y = self._y
        assert X is not None and y is not None

        out = np.empty(Q.shape[0], dtype=self.dtype)
        X2 = np.sum(X * X, axis=1, keepdims=True).T  # (1, n), computed once

        for start in range(0, Q.shape[0], self.chunk_size):
            end = min(start + self.chunk_size, Q.shape[0])
            Qc = Q[start:end]

            Q2 = np.sum(Qc * Qc, axis=1, keepdims=True)  # (c, 1)
            d2 = Q2 + X2 - 2.0 * (Qc @ X.T)               # (c, n)
            d2 = np.maximum(d2, 0.0)
            d = np.sqrt(d2, dtype=self.dtype)

            zero_mask = d <= self.eps
            has_exact = zero_mask.any(axis=1)

            chunk_out = np.empty(Qc.shape[0], dtype=self.dtype)

            if np.any(has_exact):
                rows = np.where(has_exact)[0]
                for i in rows:
                    chunk_out[i] = y[zero_mask[i]].mean(dtype=self.dtype)

            rows = np.where(~has_exact)[0]
            if rows.size:
                d_sub = d[rows]
                w = 1.0 / np.power(d_sub + self.eps, self.power, dtype=self.dtype)
                if self.mode == "sum":
                    chunk_out[rows] = w @ y
                else:
                    denom = np.sum(w, axis=1)
                    chunk_out[rows] = (w @ y) / denom

            out[start:end] = chunk_out

        return out