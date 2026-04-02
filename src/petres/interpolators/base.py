from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray


class BaseInterpolator(ABC):
    """Define a validated template for spatial interpolation workflows.

    This abstract base class centralizes input validation, fitted-state
    management, and dimensionality checks for interpolators that operate on
    coordinate/value pairs. Concrete subclasses only need to implement
    :meth:`_fit_impl` and :meth:`_predict_impl`.

    Notes
    -----
    The ``allowed_dims`` class attribute can be overridden by subclasses to
    restrict supported coordinate dimensionalities, for example ``(2,)`` for 2D
    interpolation or ``(2, 3)`` for both 2D and 3D support.
    """

    allowed_dims: Iterable[int] | None = None  # override in subclasses, e.g. (2,) or (2, 3)

    def __init__(self) -> None:
        """Initialize fitted state and dimensionality constraints."""
        self._is_fitted = False
        self.dim_: int | None = None
        self._allowed_dims: tuple[int, ...] | None

        if self.allowed_dims is not None:
            self._allowed_dims = tuple(int(d) for d in self.allowed_dims)
        else:
            self._allowed_dims = None
            
    def is_allowed_dim(self, dim: int) -> bool:
        """Check whether a dimensionality is accepted by the interpolator.

        Parameters
        ----------
        dim : int
            Coordinate dimensionality to validate.

        Returns
        -------
        bool
            ``True`` when ``dim`` is supported. If no dimensional restriction is
            configured, all dimensions are accepted.
        """
        if self._allowed_dims is None:
            return True
        return dim in self._allowed_dims
    
    def fit(self, coordinates: ArrayLike, values: ArrayLike) -> None:
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
        coordinates, values = self._validate_fit_inputs(coordinates, values)

        self.dim_ = int(coordinates.shape[1])

        self._fit_impl(coordinates, values)
        self._is_fitted = True

    def predict(self, coordinates: ArrayLike) -> NDArray[np.float64]:
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
        coordinates: NDArray[np.float64],
        values: NDArray[np.float64],
    ) -> None:
        """Fit implementation hook for subclass-specific training logic.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated coordinates with shape ``(n_samples, dim)``.
        values : numpy.ndarray
            Validated values with shape ``(n_samples,)``.
        """
        ...

    @abstractmethod
    def _predict_impl(self, coordinates: NDArray[np.float64]) -> NDArray[np.float64]:
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
        """Raise RuntimeError if the interpolator has not been fitted."""
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before prediction.")

    def _validate_fit_inputs(
        self,
        coordinates: ArrayLike,
        values: ArrayLike,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
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
        """
        coordinates = np.asarray(coordinates, dtype=float)
        values = np.asarray(values, dtype=float)

        if coordinates.ndim != 2:
            raise ValueError(f"coordinates must be 2D (n_samples, dim). Got {coordinates.shape}")
        if values.ndim != 1:
            raise ValueError(f"values must be 1D (n_samples,). Got {values.shape}")
        if coordinates.shape[0] != values.shape[0]:
            raise ValueError(
                f"coordinates and values must have same n_samples. "
                f"Got {coordinates.shape[0]} and {values.shape[0]}"
            )
        if coordinates.shape[0] == 0:
            raise ValueError("coordinates/values must contain at least 1 sample.")

        # Optional but very user-friendly in geo workflows
        if not np.isfinite(coordinates).all():
            raise ValueError("coordinates contain NaN or inf.")
        if not np.isfinite(values).all():
            raise ValueError("values contain NaN or inf.")

        dim = int(coordinates.shape[1])

        if self._allowed_dims is not None:
            if dim not in self._allowed_dims:
                raise ValueError(
                    f"{self.__class__.__name__} supports dims {self._allowed_dims}, got dim={dim}"
                )

        return coordinates, values

    def _validate_predict_inputs(self, coordinates: ArrayLike) -> NDArray[np.float64]:
        """Validate prediction coordinates against fitted model metadata.

        Parameters
        ----------
        coordinates : ArrayLike
            Candidate prediction coordinates expected as ``(n_points, dim)``.

        Returns
        -------
        numpy.ndarray
            Converted coordinates validated for prediction.
        """
        coordinates = np.asarray(coordinates, dtype=float)

        if coordinates.ndim != 2:
            raise ValueError(f"coordinates must be 2D (n_points, dim). Got {coordinates.shape}")
        if self.dim_ is None:
            raise RuntimeError("Interpolator missing fitted dim_ (internal error).")
        if coordinates.shape[1] != self.dim_:
            raise ValueError(
                f"predict dim mismatch: fitted dim={self.dim_}, got dim={coordinates.shape[1]}"
            )

        if coordinates.shape[0] == 0:
            # Returning empty prediction is often nicer than error
            return coordinates

        if not np.isfinite(coordinates).all():
            raise ValueError("predict coordinates contain NaN or inf.")

        return coordinates