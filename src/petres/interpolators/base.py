from __future__ import annotations

from numpy.typing import ArrayLike, NDArray, DTypeLike
from collections.abc import Iterable
from abc import ABC, abstractmethod
from typing import Any, Self
import numpy as np

class BaseInterpolator(ABC):
    """Provide a validated template for spatial interpolation workflows.

    This abstract base class centralizes input validation, fitted-state
    management, and dimensionality checks for interpolators that operate on
    coordinate/value pairs. Concrete subclasses only need to implement
    :meth:`_fit_impl` and :meth:`_predict_impl`.

    Attributes
    ----------
    allowed_dims : tuple[int, ...] | None
        Optional class-level dimensionality constraints. Subclasses can
        override this attribute, for example ``(2,)`` for 2D-only support or
        ``(2, 3)`` for both 2D and 3D support. ``None`` allows any dimensionality.
        
    Notes
    -----
    When ``allowed_dims`` is ``None``, any coordinate dimensionality is
    accepted.
    """

    allowed_dims: tuple[int, ...] | None = None  # override in subclasses, e.g. (2,) or (2, 3)

    def __init__(self, dtype: DTypeLike = np.float64) -> None:
        """Initialize fitted state and normalize dimensionality constraints."""
        self.dtype = np.dtype(dtype)

        self._is_fitted = False
        self.dim_: int | None = None

    def is_allowed_dim(self, dim: int) -> bool:
        """Check whether a dimensionality is accepted.

        Parameters
        ----------
        dim : int
            Coordinate dimensionality to validate. Must be an integer.

        Returns
        -------
        bool
            ``True`` when ``dim`` is supported. If no dimensional restriction is
            configured, all dimensions are accepted.
        """
        if self.allowed_dims is None:
            return True
        return dim in self.allowed_dims

    def fit(self, coordinates: ArrayLike, values: ArrayLike) -> Self:
        """Fit the interpolator using known sample coordinates and values.

        Parameters
        ----------
        coordinates : ArrayLike
            Sample coordinates with shape ``(n_samples, dim)``.
        values : ArrayLike
            Sample values with shape ``(n_samples,)`` corresponding to
            ``coordinates``.

        Raises
        ------
        ValueError
            If coordinates or values have invalid shape, mismatch in sample
            count, contain non-finite values, or violate dimensionality
            constraints.

        Examples
        --------
        >>> interp = SomeInterpolator()
        >>> interp.fit([[0.0, 0.0], [1.0, 1.0]], [10.0, 20.0])
        """
        # Validate and convert inputs to numpy arrays
        coordinates, values = self._validate_fit_inputs(coordinates, values)

        # Delegate to subclass-specific fit implementation
        self._fit_impl(coordinates, values)

        # Only update state after successful fit
        self.dim_ = int(coordinates.shape[1])
        self._is_fitted = True
        return self

    def predict(self, coordinates: ArrayLike) -> NDArray[Any]:
        """Predict interpolated values at new coordinates.

        Parameters
        ----------
        coordinates : ArrayLike
            Coordinates with shape ``(n_points, dim)`` where ``dim`` matches the
            dimensionality used during :meth:`fit`.

        Returns
        -------
        numpy.ndarray
            Predicted values with one value per input coordinate.

        Raises
        ------
        RuntimeError
            If called before the interpolator is fitted.
        ValueError
            If ``coordinates`` has invalid shape, dimensionality mismatch, or
            non-finite values.

        Examples
        --------
        >>> interp = SomeInterpolator()
        >>> interp.fit([[0.0, 0.0], [1.0, 1.0]], [10.0, 20.0])
        >>> interp.predict([[0.5, 0.5]])
        array([...])
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        return self._predict_impl(coordinates)

    @abstractmethod
    def _fit_impl(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> None:
        """Fit implementation hook.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated coordinates with shape ``(n_samples, dim)``.
        values : numpy.ndarray
            Validated values with shape ``(n_samples,)``.
        """
        ...

    @abstractmethod
    def _predict_impl(self, coordinates: NDArray[Any]) -> NDArray[Any]:
        """Prediction implementation hook for subclass-specific inference.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated prediction coordinates with shape ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Predicted values for each input coordinate.
        """
        ...

    def _check_fitted(self) -> None:
        """Validate that the interpolator has been fitted.

        Raises
        ------
        RuntimeError
            If the interpolator has not been fitted.
        """
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before prediction.")

    def _validate_fit_inputs(
        self,
        coordinates: ArrayLike,
        values: ArrayLike,
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        """Validate training input arrays.

        Parameters
        ----------
        coordinates : ArrayLike
            Candidate coordinates expected as ``(n_samples, dim)``.
        values : ArrayLike
            Candidate values expected as ``(n_samples,)``.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Converted and validated ``(coordinates, values)`` arrays with
            floating-point dtype.

        Raises
        ------
        ValueError
            If shapes are invalid, sample counts mismatch, inputs are empty, or
            values are non-finite.
        """
        # Validate coordinates
        coordinates = self._validate_coordinates(coordinates)

        # Validate values
        values = np.asarray(values, dtype=self.dtype)
        if values.ndim != 1:
            raise ValueError(f"values must be 1D (n_samples,). Got {values.shape}")
        if not np.isfinite(values).all():
            raise ValueError("values contain NaN or inf.")
        
        # Check sample count match
        if coordinates.shape[0] != values.shape[0]:
            raise ValueError(
                f"coordinates and values must have same n_samples. "
                f"Got {coordinates.shape[0]} and {values.shape[0]}"
            )
        
        return coordinates, values

    def _validate_predict_inputs(self, coordinates: ArrayLike) -> NDArray[Any]:
        """Validate prediction coordinates against fitted model metadata.

        Parameters
        ----------
        coordinates : ArrayLike
            Candidate prediction coordinates expected as ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Converted coordinates validated for prediction.

        Raises
        ------
        ValueError
            If coordinate shape is invalid, dimensionality does not match the
            fitted model, or values are non-finite.
        RuntimeError
            If fitted dimensionality metadata is unavailable.
        """
        coordinates = self._validate_coordinates(coordinates)

        if self.dim_ is None:
            raise RuntimeError("Interpolator missing fitted dim_ (internal error).")
        if coordinates.shape[1] != self.dim_:
            raise ValueError(
                f"predict dim mismatch: fitted dim={self.dim_}, got dim={coordinates.shape[1]}"
            )
        return coordinates

    def _validate_coordinates(
        self,
        coordinates: ArrayLike,
    ) -> NDArray:
        """Convert and validate coordinate array."""
        coordinates = np.asarray(coordinates, dtype=self.dtype)

        if coordinates.ndim != 2:
            raise ValueError(
                f"coordinates must be 2D (n_points, dim). "
                f"Got {coordinates.shape}"
            )
        
        if coordinates.shape[0] == 0:
            raise ValueError("Coordinates must contain at least 1 point.")
        if coordinates.shape[1] == 0:
            raise ValueError("Coordinates must contain at least 1 dimension.")

        if not np.isfinite(coordinates).all():
            raise ValueError("Coordinates contain NaN or inf.")

        dim = int(coordinates.shape[1])

        if not self.is_allowed_dim(dim):
            raise ValueError(
                f"{self.__class__.__name__} supports dims {self.allowed_dims}, got dim={dim}"
            )
            
        return coordinates
    