"""Nearest Neighbor interpolation for spatial data.

Simple and fast interpolation by assigning the value of the nearest known point.
Useful for categorical data or when smooth interpolation is not desired.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, Union, Tuple
import numpy as np
from scipy.spatial import cKDTree

from ..base import InterpolatorBase


@dataclass
class NearestNeighborInterpolator(InterpolatorBase):
    """
    Nearest Neighbor interpolator using efficient KD-tree search.
    
    Assigns to each target point the value of its closest data point.
    Fast and memory-efficient, but produces discontinuous fields.
    
    Attributes:
        metric (Literal): Distance metric for neighbor search
            'euclidean' (default), 'manhattan', 'chebyshev', 'minkowski'
        p (float): Parameter for Minkowski metric (default: 2.0)
        leafsize (int): KD-tree leaf size for performance tuning (default: 10)
        workers (int): Number of workers for parallel search (default: 1)
    
    Example:
        >>> # Interpolate facies (categorical data)
        >>> nn = NearestNeighborInterpolator()
        >>> nn.fit(well_locations, facies_codes)
        >>> grid_facies = nn.interpolate(grid_points)
    """
    
    metric: Literal['euclidean', 'manhattan', 'chebyshev', 'minkowski'] = 'euclidean'
    p: float = 2.0
    leafsize: int = 10
    workers: int = 1
    
    # Private attributes
    _kdtree: Optional[cKDTree] = field(init=False, repr=False, default=None)
    _points: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _values: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _is_fitted: bool = field(init=False, repr=False, default=False)
    
    def __post_init__(self):
        """Validate parameters."""
        if self.p <= 0:
            raise ValueError(f"p must be > 0, got {self.p}")
        if self.leafsize < 1:
            raise ValueError(f"leafsize must be >= 1, got {self.leafsize}")
        if self.workers < 1:
            raise ValueError(f"workers must be >= 1, got {self.workers}")
    
    def fit(self, points: np.ndarray, values: np.ndarray) -> 'NearestNeighborInterpolator':
        """
        Fit interpolator to known data points.
        
        Args:
            points: Known point coordinates, shape (n_points, ndim)
            values: Values at known points, shape (n_points,) or (n_points, n_features)
        
        Returns:
            self: Fitted interpolator
        
        Raises:
            ValueError: If inputs have incompatible shapes
        """
        points = np.asarray(points, dtype=np.float64)
        values = np.asarray(values)
        
        if points.ndim != 2:
            raise ValueError(f"points must be 2D array, got shape {points.shape}")
        
        if values.ndim == 1:
            if points.shape[0] != values.shape[0]:
                raise ValueError(
                    f"points and values must have same length: "
                    f"{points.shape[0]} != {values.shape[0]}"
                )
        elif values.ndim == 2:
            if points.shape[0] != values.shape[0]:
                raise ValueError(
                    f"points and values must have same first dimension: "
                    f"{points.shape[0]} != {values.shape[0]}"
                )
        else:
            raise ValueError(f"values must be 1D or 2D, got shape {values.shape}")
        
        if points.shape[0] < 1:
            raise ValueError("Need at least 1 point for interpolation")
        
        self._points = points.copy()
        self._values = values.copy()
        
        # Build KD-tree with specified metric
        if self.metric == 'euclidean':
            p_param = 2
        elif self.metric == 'manhattan':
            p_param = 1
        elif self.metric == 'minkowski':
            p_param = self.p
        else:  # chebyshev
            p_param = np.inf
        
        self._kdtree = cKDTree(
            self._points,
            leafsize=self.leafsize
        )
        
        self._is_fitted = True
        return self
    
    def interpolate(self, target_points: np.ndarray) -> np.ndarray:
        """
        Interpolate values at target points using nearest neighbor.
        
        Args:
            target_points: Target coordinates, shape (n_targets, ndim)
        
        Returns:
            Interpolated values, shape (n_targets,) or (n_targets, n_features)
        
        Raises:
            RuntimeError: If interpolator not fitted
            ValueError: If target_points has wrong dimensionality
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before interpolation")
        
        target_points = np.asarray(target_points, dtype=np.float64)
        
        if target_points.ndim != 2:
            raise ValueError(f"target_points must be 2D array, got shape {target_points.shape}")
        
        if target_points.shape[1] != self._points.shape[1]:
            raise ValueError(
                f"target_points dimensionality ({target_points.shape[1]}) must match "
                f"fitted points ({self._points.shape[1]})"
            )
        
        # Query nearest neighbors
        distances, indices = self._kdtree.query(
            target_points,
            k=1,
            workers=self.workers
        )
        
        # Return values of nearest neighbors
        result = self._values[indices]
        
        return result
    
    def interpolate_k_nearest(
        self,
        target_points: np.ndarray,
        k: int = 1,
        return_distances: bool = False
    ) -> Union[np.ndarray, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
        """
        Get k nearest neighbors for each target point.
        
        Args:
            target_points: Target coordinates, shape (n_targets, ndim)
            k: Number of nearest neighbors to return
            return_distances: If True, also return distances and indices
        
        Returns:
            If return_distances is False:
                values: Values of k nearest neighbors, shape (n_targets, k) or (n_targets, k, n_features)
            If return_distances is True:
                (values, distances, indices): Tuple of arrays
        
        Raises:
            RuntimeError: If interpolator not fitted
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before interpolation")
        
        target_points = np.asarray(target_points, dtype=np.float64)
        
        if target_points.ndim != 2:
            raise ValueError(f"target_points must be 2D array, got shape {target_points.shape}")
        
        k = min(k, len(self._points))  # Can't request more than available
        
        # Query k nearest neighbors
        distances, indices = self._kdtree.query(
            target_points,
            k=k,
            workers=self.workers
        )
        
        # Get values
        values = self._values[indices]
        
        if return_distances:
            return values, distances, indices
        else:
            return values
    
    def query_ball(
        self,
        target_points: np.ndarray,
        radius: float,
        return_distances: bool = False
    ) -> list:
        """
        Find all neighbors within radius of each target point.
        
        Args:
            target_points: Target coordinates, shape (n_targets, ndim)
            radius: Search radius
            return_distances: If True, also return distances
        
        Returns:
            List of arrays, one per target point, containing neighbor indices
            (and distances if return_distances=True)
        
        Raises:
            RuntimeError: If interpolator not fitted
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before query")
        
        target_points = np.asarray(target_points, dtype=np.float64)
        
        if target_points.ndim != 2:
            raise ValueError(f"target_points must be 2D array, got shape {target_points.shape}")
        
        if return_distances:
            # Query with distance tracking
            results = []
            for point in target_points:
                indices = self._kdtree.query_ball_point(point, radius, workers=self.workers)
                if indices:
                    dists = np.linalg.norm(self._points[indices] - point, axis=1)
                    results.append((np.array(indices), dists))
                else:
                    results.append((np.array([], dtype=int), np.array([])))
            return results
        else:
            # Query indices only
            return self._kdtree.query_ball_point(
                target_points,
                radius,
                workers=self.workers
            )
    
    def validate(self) -> bool:
        """
        Validate that interpolator is properly fitted.
        
        Returns:
            True if valid, False otherwise
        """
        if not self._is_fitted:
            return False
        
        if self._kdtree is None:
            return False
        
        if self._points is None or self._values is None:
            return False
        
        if len(self._points) != len(self._values):
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation."""
        status = "fitted" if self._is_fitted else "not fitted"
        n_points = len(self._points) if self._is_fitted else 0
        return (
            f"NearestNeighborInterpolator(metric='{self.metric}', "
            f"status={status}, n_points={n_points})"
        )
