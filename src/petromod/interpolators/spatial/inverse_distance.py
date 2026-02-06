"""Inverse Distance Weighting (IDW) interpolation.

Implements Shepard's method for spatial interpolation using weighted averages
based on inverse distance to known points. Commonly used in geostatistics and
reservoir modeling for property interpolation.
"""

from dataclasses import dataclass, field
from typing import Optional, Tuple, Union
import numpy as np
from scipy.spatial import cKDTree

from ..base import InterpolatorBase


@dataclass
class InverseDistanceWeightingInterpolator(InterpolatorBase):
    """
    Inverse Distance Weighting (IDW) interpolator.
    
    Uses Shepard's method: w_i = 1 / d_i^p where d_i is distance to point i,
    and p is the power parameter (typically 2).
    
    Attributes:
        power (float): Power parameter for distance weighting (default: 2.0)
                      Higher values give more weight to nearby points
        max_neighbors (Optional[int]): Maximum number of neighbors to use
                                       None means use all points
        radius (Optional[float]): Search radius for neighbors (None = unlimited)
        min_neighbors (int): Minimum neighbors required for interpolation
        epsilon (float): Small value to avoid division by zero
        smoothing (float): Smoothing parameter added to distances (default: 0.0)
        use_kdtree (bool): Use KD-tree for efficient nearest neighbor search
    
    Example:
        >>> # Interpolate well log data to grid
        >>> idw = InverseDistanceWeightingInterpolator(power=2.0, max_neighbors=12)
        >>> idw.fit(well_points, well_values)
        >>> grid_values = idw.interpolate(grid_points)
    """
    
    power: float = 2.0
    max_neighbors: Optional[int] = None
    radius: Optional[float] = None
    min_neighbors: int = 1
    epsilon: float = 1e-10
    smoothing: float = 0.0
    use_kdtree: bool = True
    
    # Private attributes
    _points: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _values: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _kdtree: Optional[cKDTree] = field(init=False, repr=False, default=None)
    _is_fitted: bool = field(init=False, repr=False, default=False)
    
    def __post_init__(self):
        """Validate parameters."""
        if self.power <= 0:
            raise ValueError(f"power must be > 0, got {self.power}")
        if self.min_neighbors < 1:
            raise ValueError(f"min_neighbors must be >= 1, got {self.min_neighbors}")
        if self.max_neighbors is not None and self.max_neighbors < self.min_neighbors:
            raise ValueError(
                f"max_neighbors ({self.max_neighbors}) must be >= min_neighbors ({self.min_neighbors})"
            )
        if self.smoothing < 0:
            raise ValueError(f"smoothing must be >= 0, got {self.smoothing}")
        if self.epsilon <= 0:
            raise ValueError(f"epsilon must be > 0, got {self.epsilon}")
    
    def fit(self, points: np.ndarray, values: np.ndarray) -> 'InverseDistanceWeightingInterpolator':
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
        values = np.asarray(values, dtype=np.float64)
        
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
            raise ValueError(f"values must be 1D or 2D array, got shape {values.shape}")
        
        if points.shape[0] < self.min_neighbors:
            raise ValueError(
                f"Need at least {self.min_neighbors} points, got {points.shape[0]}"
            )
        
        self._points = points.copy()
        self._values = values.copy()
        
        # Build KD-tree for efficient nearest neighbor search
        if self.use_kdtree:
            self._kdtree = cKDTree(self._points)
        
        self._is_fitted = True
        return self
    
    def interpolate(self, target_points: np.ndarray) -> np.ndarray:
        """
        Interpolate values at target points.
        
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
        
        n_targets = target_points.shape[0]
        output_shape = (n_targets,) if self._values.ndim == 1 else (n_targets, self._values.shape[1])
        result = np.zeros(output_shape, dtype=np.float64)
        
        for i in range(n_targets):
            result[i] = self._interpolate_single(target_points[i])
        
        return result
    
    def _interpolate_single(self, target: np.ndarray) -> Union[float, np.ndarray]:
        """Interpolate value at a single target point."""
        # Find neighbors
        if self.use_kdtree and self._kdtree is not None:
            distances, indices = self._query_neighbors_kdtree(target)
        else:
            distances, indices = self._query_neighbors_bruteforce(target)
        
        # Handle exact match
        if distances[0] < self.epsilon:
            return self._values[indices[0]].copy()
        
        # Check minimum neighbors
        if len(indices) < self.min_neighbors:
            # Fallback: use nearest neighbor or NaN
            if len(indices) > 0:
                return self._values[indices[0]].copy()
            else:
                return np.nan if self._values.ndim == 1 else np.full(self._values.shape[1], np.nan)
        
        # Compute weights
        weights = self._compute_weights(distances)
        
        # Normalize weights
        weight_sum = np.sum(weights)
        if weight_sum < self.epsilon:
            # Degenerate case: use nearest neighbor
            return self._values[indices[0]].copy()
        
        weights /= weight_sum
        
        # Weighted average
        if self._values.ndim == 1:
            return np.sum(weights * self._values[indices])
        else:
            return np.sum(weights[:, np.newaxis] * self._values[indices], axis=0)
    
    def _query_neighbors_kdtree(self, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Query neighbors using KD-tree."""
        k = self.max_neighbors if self.max_neighbors is not None else len(self._points)
        k = min(k, len(self._points))
        
        if self.radius is not None:
            # Query within radius
            distances, indices = self._kdtree.query(
                target, k=k, distance_upper_bound=self.radius
            )
            # Filter out invalid results
            valid = np.isfinite(distances)
            distances = distances[valid]
            indices = indices[valid]
        else:
            # Query k nearest
            distances, indices = self._kdtree.query(target, k=k)
        
        return distances, indices
    
    def _query_neighbors_bruteforce(self, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Query neighbors using brute force distance computation."""
        # Compute all distances
        distances = np.linalg.norm(self._points - target, axis=1)
        
        # Apply radius filter if specified
        if self.radius is not None:
            valid = distances <= self.radius
            distances = distances[valid]
            indices = np.where(valid)[0]
        else:
            indices = np.arange(len(distances))
        
        # Sort by distance
        sort_idx = np.argsort(distances)
        distances = distances[sort_idx]
        indices = indices[sort_idx]
        
        # Limit to max_neighbors
        if self.max_neighbors is not None:
            distances = distances[:self.max_neighbors]
            indices = indices[:self.max_neighbors]
        
        return distances, indices
    
    def _compute_weights(self, distances: np.ndarray) -> np.ndarray:
        """Compute inverse distance weights."""
        # Add smoothing to avoid singularities
        smoothed_distances = distances + self.smoothing
        
        # Inverse distance weighting
        weights = 1.0 / np.power(smoothed_distances, self.power)
        
        return weights
    
    def validate(self) -> bool:
        """
        Validate that interpolator is properly configured and fitted.
        
        Returns:
            True if valid, False otherwise
        """
        if not self._is_fitted:
            return False
        
        if self._points is None or self._values is None:
            return False
        
        if len(self._points) != len(self._values):
            return False
        
        return True
    
    def cross_validate(self, k_folds: int = 5) -> float:
        """
        Perform k-fold cross-validation.
        
        Args:
            k_folds: Number of folds for cross-validation
        
        Returns:
            Mean absolute error across all folds
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before cross-validation")
        
        n_points = len(self._points)
        indices = np.arange(n_points)
        np.random.shuffle(indices)
        
        fold_size = n_points // k_folds
        errors = []
        
        for fold in range(k_folds):
            # Split data
            test_start = fold * fold_size
            test_end = (fold + 1) * fold_size if fold < k_folds - 1 else n_points
            test_idx = indices[test_start:test_end]
            train_idx = np.concatenate([indices[:test_start], indices[test_end:]])
            
            # Fit on training data
            temp_interp = InverseDistanceWeightingInterpolator(
                power=self.power,
                max_neighbors=self.max_neighbors,
                radius=self.radius,
                min_neighbors=self.min_neighbors,
                epsilon=self.epsilon,
                smoothing=self.smoothing,
                use_kdtree=self.use_kdtree
            )
            temp_interp.fit(self._points[train_idx], self._values[train_idx])
            
            # Predict on test data
            predictions = temp_interp.interpolate(self._points[test_idx])
            
            # Compute error
            error = np.mean(np.abs(predictions - self._values[test_idx]))
            errors.append(error)
        
        return np.mean(errors)
    
    def __repr__(self) -> str:
        """String representation."""
        status = "fitted" if self._is_fitted else "not fitted"
        n_points = len(self._points) if self._is_fitted else 0
        return (
            f"InverseDistanceWeightingInterpolator(power={self.power}, "
            f"max_neighbors={self.max_neighbors}, "
            f"radius={self.radius}, "
            f"status={status}, n_points={n_points})"
        )
