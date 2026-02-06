"""Radial Basis Function (RBF) interpolation.

Implements various radial basis functions for smooth spatial interpolation.
Particularly useful for scattered data in geoscience applications.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal, Callable
import numpy as np
from scipy.spatial.distance import cdist
from scipy.linalg import solve

from ..base import InterpolatorBase


# Standard RBF kernel functions
def gaussian(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Gaussian RBF: exp(-(epsilon*r)^2)"""
    return np.exp(-(epsilon * r) ** 2)


def multiquadric(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Multiquadric RBF: sqrt(1 + (epsilon*r)^2)"""
    return np.sqrt(1 + (epsilon * r) ** 2)


def inverse_multiquadric(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Inverse multiquadric RBF: 1/sqrt(1 + (epsilon*r)^2)"""
    return 1.0 / np.sqrt(1 + (epsilon * r) ** 2)


def thin_plate_spline(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Thin plate spline RBF: r^2 * log(r)"""
    # Avoid log(0) by adding small epsilon
    r_safe = np.where(r < 1e-10, 1e-10, r)
    return r_safe ** 2 * np.log(r_safe)


def cubic(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Cubic RBF: r^3"""
    return r ** 3


def quintic(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Quintic RBF: r^5"""
    return r ** 5


def linear(r: np.ndarray, epsilon: float) -> np.ndarray:
    """Linear RBF: r"""
    return r


RBF_KERNELS = {
    'gaussian': gaussian,
    'multiquadric': multiquadric,
    'inverse_multiquadric': inverse_multiquadric,
    'thin_plate_spline': thin_plate_spline,
    'cubic': cubic,
    'quintic': quintic,
    'linear': linear,
}


@dataclass
class RadialBasisFunctionInterpolator(InterpolatorBase):
    """
    Radial Basis Function (RBF) interpolator.
    
    Constructs smooth interpolant using radial basis functions:
    f(x) = sum_i w_i * phi(||x - x_i||) + p(x)
    
    where phi is the RBF kernel, w_i are weights, and p(x) is optional polynomial.
    
    Attributes:
        kernel (str): RBF kernel function name:
            'gaussian', 'multiquadric', 'inverse_multiquadric',
            'thin_plate_spline', 'cubic', 'quintic', 'linear'
        epsilon (float): Shape parameter for RBF (default: 1.0)
                        Smaller values = smoother interpolation
        smoothing (float): Smoothing parameter (default: 0.0)
                          Larger values allow more deviation from data
        polynomial_degree (Optional[int]): Degree of polynomial tail
                                          None, 0, 1, 2, or 3
        norm (str): Distance metric ('euclidean' or 'cityblock')
    
    Example:
        >>> # Smooth interpolation of reservoir properties
        >>> rbf = RadialBasisFunctionInterpolator(kernel='multiquadric', epsilon=0.5)
        >>> rbf.fit(well_locations, porosity_values)
        >>> grid_porosity = rbf.interpolate(grid_points)
    """
    
    kernel: Literal[
        'gaussian', 'multiquadric', 'inverse_multiquadric',
        'thin_plate_spline', 'cubic', 'quintic', 'linear'
    ] = 'multiquadric'
    epsilon: float = 1.0
    smoothing: float = 0.0
    polynomial_degree: Optional[int] = None
    norm: Literal['euclidean', 'cityblock'] = 'euclidean'
    
    # Private attributes
    _points: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _values: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _weights: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _poly_coeffs: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _kernel_func: Optional[Callable] = field(init=False, repr=False, default=None)
    _is_fitted: bool = field(init=False, repr=False, default=False)
    
    def __post_init__(self):
        """Validate parameters."""
        if self.kernel not in RBF_KERNELS:
            raise ValueError(
                f"Unknown kernel '{self.kernel}'. "
                f"Choose from: {list(RBF_KERNELS.keys())}"
            )
        
        if self.epsilon <= 0:
            raise ValueError(f"epsilon must be > 0, got {self.epsilon}")
        
        if self.smoothing < 0:
            raise ValueError(f"smoothing must be >= 0, got {self.smoothing}")
        
        if self.polynomial_degree is not None:
            if not isinstance(self.polynomial_degree, int) or self.polynomial_degree < 0:
                raise ValueError(
                    f"polynomial_degree must be None or non-negative int, "
                    f"got {self.polynomial_degree}"
                )
            if self.polynomial_degree > 3:
                raise ValueError(
                    f"polynomial_degree must be <= 3, got {self.polynomial_degree}"
                )
        
        self._kernel_func = RBF_KERNELS[self.kernel]
    
    def fit(self, points: np.ndarray, values: np.ndarray) -> 'RadialBasisFunctionInterpolator':
        """
        Fit RBF interpolator to known data points.
        
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
            values = values[:, np.newaxis]  # Make 2D for consistency
        elif values.ndim == 2:
            if points.shape[0] != values.shape[0]:
                raise ValueError(
                    f"points and values must have same first dimension: "
                    f"{points.shape[0]} != {values.shape[0]}"
                )
        else:
            raise ValueError(f"values must be 1D or 2D, got shape {values.shape}")
        
        n_points, ndim = points.shape
        n_features = values.shape[1]
        
        # Check sufficient points for polynomial
        if self.polynomial_degree is not None:
            min_points = self._get_polynomial_terms(ndim)
            if n_points < min_points:
                raise ValueError(
                    f"Need at least {min_points} points for polynomial degree "
                    f"{self.polynomial_degree} in {ndim}D, got {n_points}"
                )
        
        self._points = points.copy()
        self._values = values.copy()
        
        # Build RBF matrix
        distances = cdist(points, points, metric=self.norm)
        A = self._kernel_func(distances, self.epsilon)
        
        # Add smoothing on diagonal
        if self.smoothing > 0:
            A[np.diag_indices_from(A)] += self.smoothing
        
        # Add polynomial terms if requested
        if self.polynomial_degree is not None:
            P = self._build_polynomial_matrix(points)
            n_poly = P.shape[1]
            
            # Augmented system: [A P; P^T 0] [w; c] = [y; 0]
            n_total = n_points + n_poly
            A_aug = np.zeros((n_total, n_total))
            A_aug[:n_points, :n_points] = A
            A_aug[:n_points, n_points:] = P
            A_aug[n_points:, :n_points] = P.T
            
            b_aug = np.zeros((n_total, n_features))
            b_aug[:n_points] = values
            
            # Solve augmented system
            solution = solve(A_aug, b_aug, assume_a='sym')
            
            self._weights = solution[:n_points]
            self._poly_coeffs = solution[n_points:]
        else:
            # Solve RBF system only
            self._weights = solve(A, values, assume_a='sym')
            self._poly_coeffs = None
        
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
        
        if target_points.shape[1] != self._points.shape[1]:
            raise ValueError(
                f"target_points dimensionality ({target_points.shape[1]}) must match "
                f"fitted points ({self._points.shape[1]})"
            )
        
        # Compute distances to all data points
        distances = cdist(target_points, self._points, metric=self.norm)
        
        # Apply RBF kernel
        rbf_matrix = self._kernel_func(distances, self.epsilon)
        
        # Compute RBF contribution
        result = rbf_matrix @ self._weights
        
        # Add polynomial contribution if present
        if self._poly_coeffs is not None:
            P = self._build_polynomial_matrix(target_points)
            result += P @ self._poly_coeffs
        
        # Return 1D if original values were 1D
        if self._values.shape[1] == 1:
            result = result.ravel()
        
        return result
    
    def _build_polynomial_matrix(self, points: np.ndarray) -> np.ndarray:
        """Build polynomial term matrix."""
        n_points, ndim = points.shape
        
        if self.polynomial_degree is None:
            return np.zeros((n_points, 0))
        
        if self.polynomial_degree == 0:
            # Constant: [1]
            return np.ones((n_points, 1))
        
        if self.polynomial_degree == 1:
            # Linear: [1, x, y, z, ...]
            return np.hstack([np.ones((n_points, 1)), points])
        
        if self.polynomial_degree == 2:
            # Quadratic: [1, x, y, x^2, xy, y^2, ...]
            terms = [np.ones((n_points, 1)), points]
            for i in range(ndim):
                for j in range(i, ndim):
                    terms.append((points[:, i] * points[:, j])[:, np.newaxis])
            return np.hstack(terms)
        
        # Cubic (degree 3)
        # This gets complex; for simplicity, use degree 1 polynomial for now
        # Full implementation would include all cubic terms
        return np.hstack([np.ones((n_points, 1)), points])
    
    def _get_polynomial_terms(self, ndim: int) -> int:
        """Get number of polynomial terms."""
        if self.polynomial_degree is None:
            return 0
        if self.polynomial_degree == 0:
            return 1
        if self.polynomial_degree == 1:
            return 1 + ndim
        if self.polynomial_degree == 2:
            return 1 + ndim + (ndim * (ndim + 1)) // 2
        # Cubic
        return 1 + ndim  # Simplified
    
    def validate(self) -> bool:
        """
        Validate that interpolator is properly fitted.
        
        Returns:
            True if valid, False otherwise
        """
        if not self._is_fitted:
            return False
        
        if self._points is None or self._values is None or self._weights is None:
            return False
        
        if len(self._points) != len(self._values):
            return False
        
        if len(self._points) != len(self._weights):
            return False
        
        return True
    
    def __repr__(self) -> str:
        """String representation."""
        status = "fitted" if self._is_fitted else "not fitted"
        n_points = len(self._points) if self._is_fitted else 0
        return (
            f"RadialBasisFunctionInterpolator(kernel='{self.kernel}', "
            f"epsilon={self.epsilon}, "
            f"polynomial_degree={self.polynomial_degree}, "
            f"status={status}, n_points={n_points})"
        )
