"""Linear interpolation methods for spatial data.

Implements triangulation-based linear (barycentric) interpolation in 2D/3D
and multilinear interpolation for structured grids.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import LinearNDInterpolator, RegularGridInterpolator

from ..base import InterpolatorBase


@dataclass
class LinearInterpolator(InterpolatorBase):
    """
    Linear spatial interpolation using triangulation (unstructured) or
    regular grid (structured) methods.
    
    For unstructured data, uses Delaunay triangulation and barycentric
    coordinates. For structured grids, uses multilinear interpolation.
    
    Attributes:
        method (Literal['delaunay', 'regular']): Interpolation method
            'delaunay': Unstructured triangulation-based (default)
            'regular': Structured grid with multilinear interpolation
        fill_value (float): Value for points outside convex hull (default: NaN)
        rescale (bool): Rescale points to unit cube before interpolation
                       Improves numerical stability (default: False)
    
    Example:
        >>> # Unstructured interpolation
        >>> interp = LinearInterpolator(method='delaunay')
        >>> interp.fit(scattered_points, values)
        >>> result = interp.interpolate(query_points)
        
        >>> # Structured grid interpolation
        >>> interp = LinearInterpolator(method='regular')
        >>> interp.fit_grid(x_coords, y_coords, z_coords, grid_values)
        >>> result = interp.interpolate(query_points)
    """
    
    method: Literal['delaunay', 'regular'] = 'delaunay'
    fill_value: float = np.nan
    rescale: bool = False
    
    # Private attributes
    _interpolator: Optional[object] = field(init=False, repr=False, default=None)
    _points: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _values: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _is_fitted: bool = field(init=False, repr=False, default=False)
    
    def fit(self, points: np.ndarray, values: np.ndarray) -> 'LinearInterpolator':
        """
        Fit interpolator to unstructured data points.
        
        Args:
            points: Point coordinates, shape (n_points, ndim)
            values: Values at points, shape (n_points,) or (n_points, n_features)
        
        Returns:
            self: Fitted interpolator
        
        Raises:
            ValueError: If method is not 'delaunay' or inputs have wrong shape
        """
        if self.method != 'delaunay':
            raise ValueError(
                f"fit() only supports method='delaunay', got '{self.method}'. "
                "Use fit_grid() for regular grids."
            )
        
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
            raise ValueError(f"values must be 1D or 2D, got shape {values.shape}")
        
        # Minimum points for triangulation
        min_points = points.shape[1] + 1  # ndim + 1
        if points.shape[0] < min_points:
            raise ValueError(
                f"Need at least {min_points} points for {points.shape[1]}D triangulation, "
                f"got {points.shape[0]}"
            )
        
        self._points = points.copy()
        self._values = values.copy()
        
        # Create LinearNDInterpolator (uses Delaunay triangulation)
        self._interpolator = LinearNDInterpolator(
            points, values, fill_value=self.fill_value, rescale=self.rescale
        )
        
        self._is_fitted = True
        return self
    
    def fit_grid(
        self,
        *coords: np.ndarray,
        values: np.ndarray,
    ) -> 'LinearInterpolator':
        """
        Fit interpolator to structured grid data.
        
        Args:
            *coords: 1D coordinate arrays for each dimension
                    e.g., (x, y, z) for 3D grid
            values: Grid values, shape matching coordinate arrays
        
        Returns:
            self: Fitted interpolator
        
        Raises:
            ValueError: If method is not 'regular' or inputs incompatible
        
        Example:
            >>> x = np.linspace(0, 10, 11)
            >>> y = np.linspace(0, 5, 6)
            >>> z = np.linspace(0, 3, 4)
            >>> grid_values = np.random.rand(11, 6, 4)
            >>> interp.fit_grid(x, y, z, values=grid_values)
        """
        if self.method != 'regular':
            raise ValueError(
                f"fit_grid() only supports method='regular', got '{self.method}'. "
                "Use fit() for unstructured data."
            )
        
        if not coords:
            raise ValueError("Must provide at least one coordinate array")
        
        coords = tuple(np.asarray(c, dtype=np.float64) for c in coords)
        values = np.asarray(values, dtype=np.float64)
        
        # Validate coordinate arrays
        for i, coord in enumerate(coords):
            if coord.ndim != 1:
                raise ValueError(f"Coordinate array {i} must be 1D, got shape {coord.shape}")
            if len(coord) < 2:
                raise ValueError(f"Coordinate array {i} must have at least 2 points")
        
        # Validate values shape
        expected_shape = tuple(len(c) for c in coords)
        if values.shape[:len(coords)] != expected_shape:
            raise ValueError(
                f"values shape {values.shape[:len(coords)]} does not match "
                f"coordinate grid shape {expected_shape}"
            )
        
        # Store for reference
        self._points = coords
        self._values = values.copy()
        
        # Create RegularGridInterpolator
        self._interpolator = RegularGridInterpolator(
            coords,
            values,
            method='linear',
            bounds_error=False,
            fill_value=self.fill_value
        )
        
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
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before interpolation")
        
        target_points = np.asarray(target_points, dtype=np.float64)
        
        if target_points.ndim != 2:
            raise ValueError(f"target_points must be 2D array, got shape {target_points.shape}")
        
        # Use scipy interpolators
        result = self._interpolator(target_points)
        
        return result
    
    def validate(self) -> bool:
        """
        Validate that interpolator is properly fitted.
        
        Returns:
            True if valid, False otherwise
        """
        if not self._is_fitted:
            return False
        
        if self._interpolator is None:
            return False
        
        if self._points is None or self._values is None:
            return False
        
        return True
    
    def get_triangulation(self) -> Optional[Delaunay]:
        """
        Get the Delaunay triangulation (only for method='delaunay').
        
        Returns:
            Delaunay triangulation object or None
        """
        if self.method != 'delaunay' or not self._is_fitted:
            return None
        
        if hasattr(self._interpolator, 'tri'):
            return self._interpolator.tri
        
        return None
    
    def __repr__(self) -> str:
        """String representation."""
        status = "fitted" if self._is_fitted else "not fitted"
        if self._is_fitted and self.method == 'delaunay':
            n_points = len(self._points)
            return f"LinearInterpolator(method='{self.method}', status={status}, n_points={n_points})"
        elif self._is_fitted and self.method == 'regular':
            grid_shape = tuple(len(c) for c in self._points)
            return f"LinearInterpolator(method='{self.method}', status={status}, grid_shape={grid_shape})"
        else:
            return f"LinearInterpolator(method='{self.method}', status={status})"
