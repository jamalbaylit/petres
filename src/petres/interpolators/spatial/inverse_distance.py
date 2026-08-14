from __future__ import annotations

from numpy.typing import DTypeLike, NDArray
from scipy.spatial.distance import cdist
from scipy.spatial import cKDTree
from typing import Any
import numpy as np

from ..._utils._chunking import iter_chunks
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
    dtype : numpy.dtype or str, default numpy.float64
        Storage dtype for cached arrays and outputs.
    chunk_size : int or None, default None
        Upper bound on query points processed per batch. 
        If None, all samples are processed at once.
    """

    allowed_dims = None # allow any dim
    
    def __init__(
        self,
        *,
        dtype: DTypeLike = np.float64,
        power: float = 2.0,
        eps: float = 1e-12,
        neighbors: int | None = None,
        chunk_size: int | None= None,
    ) -> None:
        """Initialize the interpolator with validated IDW configuration.

        Raises
        ------
        ValueError
            If ``power <= 0``, ``eps <= 0``, ``neighbors`` is not positive
            when provided, or ``chunk_size <= 0``.

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
        if chunk_size is not None and chunk_size <= 0:
            raise ValueError(f"`chunk_size` must be > 0. Got {chunk_size}.")

        self.power = float(power)
        self.eps = float(eps)
        self.neighbors = int(neighbors) if neighbors is not None else None
        self.chunk_size = int(chunk_size) if chunk_size is not None else None

        # fitted state
        self._coords: np.ndarray | None = None  # (n, dim)
        self._vals: np.ndarray | None = None  # (n,)
        self._tree: cKDTree | None = None

    def _fit_impl(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
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
            If ``neighbors`` exceeds the number of fitted samples.
        """
        coords = coordinates
        vals = values

        if self.neighbors is not None and self.neighbors > coords.shape[0]:
            raise ValueError(
                f"`neighbors`={self.neighbors} cannot be greater than n_samples={coords.shape[0]}."
            )

        # Store fitted data and build KD-tree if needed. The KD-tree is only used
        # when neighbors is set; otherwise we do brute-force distance calculations.
        self._coords = coords if self.neighbors is None else None
        self._tree = cKDTree(coords) if self.neighbors is not None else None
        self._vals = vals # required to store for prediction in both cases

    def _predict_impl(self, coordinates: NDArray[Any]) -> NDArray[Any]:
        """Predict values for query coordinates using IDW weighting.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Shape ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_points,)``.

        """
        coords = coordinates

        if self.neighbors is not None:
            return self._predict_knn(coords)
        return self._predict_full(coords)

    def _predict_knn(self, Q: NDArray[Any]) -> NDArray[Any]:
        """KD-tree-backed k-nearest-neighbor IDW. O(m log n) time, O(m*k) memory."""
        y = self._vals
        k = self.neighbors
        assert self._tree is not None and y is not None and k is not None

        out = np.empty(Q.shape[0], dtype=self.dtype)
        for slc, Qc in iter_chunks(Q, self.chunk_size):
            d_knn, idx = self._tree.query(Qc, k=k, workers=-1)
            # When k == 1, scipy returns 1D arrays; normalize to 2D (m, 1).
            if k == 1:
                d_knn = d_knn[:, None]
                idx = idx[:, None]

            y_knn = y[idx]
            w = 1.0 / np.power(d_knn + self.eps, self.power, dtype=self.dtype)
            out[slc] = np.sum(w * y_knn, axis=1) / np.sum(w, axis=1)
        return out

    def _predict_full(self, Q: NDArray[Any]) -> NDArray[Any]:
        """Brute-force IDW over all fitted samples, processed in row chunks
        to bound peak memory to roughly chunk_size * n_samples floats."""
        X = self._coords
        y = self._vals

        assert X is not None and y is not None

        out = np.empty(Q.shape[0], dtype=self.dtype)
        for slc, Qc in iter_chunks(Q, self.chunk_size):
            d = cdist(Qc, X, metric="euclidean")
            # weights = 1.0 / np.power(np.maximum(d, self.eps), self.power)
            weights = 1.0 / np.power(d + self.eps, self.power, dtype=self.dtype)
            out[slc] = (weights @ y) / np.sum(weights, axis=1)
        return out
