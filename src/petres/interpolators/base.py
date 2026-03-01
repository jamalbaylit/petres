from __future__ import annotations

from typing import Iterable, Optional
from abc import ABC, abstractmethod
import numpy as np


class BaseInterpolator(ABC):
    """
    Abstract base class for spatial interpolators.

    coordinates: (n_samples, dim)
    values:      (n_samples,)
    """

    allowed_dims: Optional[Iterable[int]] = None  # override in subclasses, e.g. (2,) or (2, 3)

    def __init__(self):
        self._is_fitted = False
        self.dim_: Optional[int] = None

        if self.allowed_dims is not None:
            self._allowed_dims = tuple(int(d) for d in self.allowed_dims)
        else:
            self._allowed_dims = None
            
    def is_allowed_dim(self, dim: int) -> bool:
        if self._allowed_dims is None:
            return True
        return dim in self._allowed_dims
    
    def fit(self, coordinates: np.ndarray, values: np.ndarray) -> None:
        coordinates, values = self._validate_fit_inputs(coordinates, values)

        self.dim_ = int(coordinates.shape[1])

        self._fit_impl(coordinates, values)
        self._is_fitted = True

    def predict(self, coordinates: np.ndarray) -> np.ndarray:
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        return self._predict_impl(coordinates)

    @abstractmethod
    def _fit_impl(self, coordinates: np.ndarray, values: np.ndarray) -> None:
        ...

    @abstractmethod
    def _predict_impl(self, coordinates: np.ndarray) -> np.ndarray:
        ...

    def _check_fitted(self):
        if not self._is_fitted:
            raise RuntimeError("Interpolator must be fitted before prediction.")

    def _validate_fit_inputs(self, coordinates: np.ndarray, values: np.ndarray):
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

    def _validate_predict_inputs(self, coordinates: np.ndarray):
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