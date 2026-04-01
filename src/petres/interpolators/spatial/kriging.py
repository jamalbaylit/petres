from __future__ import annotations

from abc import abstractmethod
from typing import Any, Callable, Iterable, Literal, Optional, Sequence

import numpy as np

from ..base import BaseInterpolator

try:
    from pykrige.ok import OrdinaryKriging
    from pykrige.ok3d import OrdinaryKriging3D
    from pykrige.uk import UniversalKriging
    from pykrige.uk3d import UniversalKriging3D
except ImportError:  # pragma: no cover
    OrdinaryKriging = None
    OrdinaryKriging3D = None
    UniversalKriging = None
    UniversalKriging3D = None


VariogramModel = Literal[
    "linear",
    "power",
    "gaussian",
    "spherical",
    "exponential",
    "hole-effect",
    "custom",
]

Backend = Literal["vectorized", "loop", "C"]


class BasePyKrigeInterpolator(BaseInterpolator):
    """Provide a common PyKrige-backed point interpolation API.

    This base class adapts PyKrige model classes to the ``BaseInterpolator``
    contract. It handles dependency checks, common model configuration, and
    shared point-execution logic for both ordinary and universal kriging.

    Notes
    -----
    Only point prediction mode is supported. Grid-style execution is
    intentionally omitted to keep the API aligned with point-based workflows.
    """

    allowed_dims = (2, 3)

    def __init__(
        self,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: Optional[dict[str, Any] | Sequence[float]] = None,
        variogram_function: Optional[Callable[..., Any]] = None,
        nlags: int = 6,
        weight: bool = False,
        verbose: bool = False,
        enable_plotting: bool = False,
        exact_values: bool = True,
        pseudo_inv: bool = False,
        pseudo_inv_type: str = "pinv",
        backend: Backend = "vectorized",
    ) -> None:
        """Initialize shared kriging options.

        Parameters
        ----------
        variogram_model : {"linear", "power", "gaussian", "spherical", "exponential", "hole-effect", "custom"}, default="linear"
            Variogram model name forwarded to the PyKrige backend model.
        variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
            Explicit variogram parameters. If ``None``, PyKrige estimates the
            parameters from input data.
        variogram_function : callable or None, default=None
            Custom variogram function used when ``variogram_model="custom"``.
        nlags : int, default=6
            Number of lag bins used for variogram estimation.
        weight : bool, default=False
            Whether semivariances are weighted during variogram fitting.
        verbose : bool, default=False
            Whether backend model construction and solve steps emit logs.
        enable_plotting : bool, default=False
            Whether PyKrige variogram fitting plots are enabled.
        exact_values : bool, default=True
            Whether interpolation reproduces training values exactly.
        pseudo_inv : bool, default=False
            Whether to use a pseudo-inverse while solving the kriging system.
        pseudo_inv_type : {"pinv", "pinvh"}, default="pinv"
            Pseudo-inverse algorithm used when ``pseudo_inv=True``.
        backend : {"vectorized", "loop", "C"}, default="vectorized"
            PyKrige execution backend for prediction calls.

        Raises
        ------
        ValueError
            If ``nlags < 1``, ``pseudo_inv_type`` is unsupported, or ``backend``
            is not one of the accepted values.
        """
        super().__init__()

        if nlags < 1:
            raise ValueError(f"`nlags` must be >= 1. Got {nlags}.")
        if pseudo_inv_type not in {"pinv", "pinvh"}:
            raise ValueError(
                f"`pseudo_inv_type` must be 'pinv' or 'pinvh'. Got {pseudo_inv_type!r}."
            )
        if backend not in {"vectorized", "loop", "C"}:
            raise ValueError(
                f"`backend` must be 'vectorized', 'loop', or 'C'. Got {backend!r}."
            )

        self.variogram_model = variogram_model
        self.variogram_parameters = variogram_parameters
        self.variogram_function = variogram_function
        self.nlags = int(nlags)
        self.weight = bool(weight)
        self.verbose = bool(verbose)
        self.enable_plotting = bool(enable_plotting)
        self.exact_values = bool(exact_values)
        self.pseudo_inv = bool(pseudo_inv)
        self.pseudo_inv_type = pseudo_inv_type
        self.backend = backend

        self._model: Any = None
        self._fit_coordinates: Optional[np.ndarray] = None
        self._fit_values: Optional[np.ndarray] = None

    def _fit_impl(self, coordinates: np.ndarray, values: np.ndarray) -> None:
        """Fit the wrapped PyKrige model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Training target values with shape ``(n_samples,)``.

        Returns
        -------
        None
            This method stores the fitted backend model on the instance.
        """
        self._ensure_pykrige_installed()

        self._fit_coordinates = np.asarray(coordinates, dtype=float)
        self._fit_values = np.asarray(values, dtype=float)
        self._model = self._build_model(self._fit_coordinates, self._fit_values)

    def _predict_impl(self, coordinates: np.ndarray) -> np.ndarray:
        """Predict values for query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_queries,)``.
        """
        predictions, _ = self._execute_points(coordinates)
        return predictions

    def predict_variance(self, coordinates: np.ndarray, **execute_kwargs: Any) -> np.ndarray:
        """Predict kriging variance for query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        numpy.ndarray
            Kriging variance values with shape ``(n_queries,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        _, variance = self._execute_points(coordinates, **execute_kwargs)
        return variance

    def predict_with_variance(
        self,
        coordinates: np.ndarray,
        **execute_kwargs: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Predict values and kriging variance for query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Two arrays ``(prediction, variance)``, each shaped ``(n_queries,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        return self._execute_points(coordinates, **execute_kwargs)

    def _execute_points(
        self,
        coordinates: np.ndarray,
        **execute_kwargs: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Execute point-based kriging on the backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Prediction and variance arrays with shape ``(n_queries,)``.

        Raises
        ------
        RuntimeError
            If the interpolator has no backend model or an unsupported fitted
            dimensionality.
        """
        if coordinates.shape[0] == 0:
            empty = np.empty((0,), dtype=float)
            return empty, empty

        if self._model is None:
            raise RuntimeError("Interpolator missing fitted PyKrige model (internal error).")

        if self.dim_ == 2:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            pred, var = self._model.execute(
                "points",
                x,
                y,
                backend=self.backend,
                **execute_kwargs,
            )
        elif self.dim_ == 3:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]
            pred, var = self._model.execute(
                "points",
                x,
                y,
                z,
                backend=self.backend,
                **execute_kwargs,
            )
        else:  # pragma: no cover
            raise RuntimeError(f"Unsupported fitted dim_: {self.dim_}")

        return np.asarray(pred, dtype=float).ravel(), np.asarray(var, dtype=float).ravel()

    @abstractmethod
    def _build_model(self, coordinates: np.ndarray, values: np.ndarray) -> Any:
        """Build and return a fitted backend kriging model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Training target values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            Backend-specific fitted kriging model instance.
        """
        ...

    @staticmethod
    def _normalize_3d_scaling(value: float | tuple[float, float]) -> tuple[float, float]:
        """Normalize 3D anisotropy scaling input to ``(scaling_y, scaling_z)``.

        Parameters
        ----------
        value : float or tuple[float, float]
            User-provided 3D anisotropy scaling.

        Returns
        -------
        tuple[float, float]
            Scaling factors for y and z axes.

        Raises
        ------
        ValueError
            If tuple input does not have length 2.
        """
        if np.isscalar(value):
            v = float(value)
            return v, v

        if len(value) != 2:
            raise ValueError(
                "`anisotropy_scaling` for 3D must be a float or a tuple of length 2 "
                "(scaling_y, scaling_z)."
            )

        return float(value[0]), float(value[1])

    @staticmethod
    def _normalize_3d_angles(
        value: float | tuple[float, float, float],
    ) -> tuple[float, float, float]:
        """Normalize 3D anisotropy angle input to ``(angle_x, angle_y, angle_z)``.

        Parameters
        ----------
        value : float or tuple[float, float, float]
            User-provided 3D anisotropy rotation angles.

        Returns
        -------
        tuple[float, float, float]
            Rotation angles around x, y, and z axes.

        Raises
        ------
        ValueError
            If tuple input does not have length 3.
        """
        if np.isscalar(value):
            v = float(value)
            return v, v, v

        if len(value) != 3:
            raise ValueError(
                "`anisotropy_angle` for 3D must be a float or a tuple of length 3 "
                "(angle_x, angle_y, angle_z)."
            )

        return float(value[0]), float(value[1]), float(value[2])

    @staticmethod
    def _ensure_pykrige_installed() -> None:
        """Validate that PyKrige optional dependencies are available.

        Returns
        -------
        None
            Completes silently when required classes are importable.

        Raises
        ------
        ImportError
            If any required PyKrige class is unavailable.
        """
        if (
            OrdinaryKriging is None
            or OrdinaryKriging3D is None
            or UniversalKriging is None
            or UniversalKriging3D is None
        ):
            raise ImportError(
                "PyKrige is required for kriging interpolators. "
                "Install it with: pip install pykrige"
            )


class OrdinaryKrigingInterpolator(BasePyKrigeInterpolator):
    """Interpolate scalar values using ordinary kriging in 2D or 3D.

    This wrapper selects ``pykrige.ok.OrdinaryKriging`` for 2D inputs and
    ``pykrige.ok3d.OrdinaryKriging3D`` for 3D inputs.
    """

    def __init__(
        self,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: Optional[dict[str, Any] | Sequence[float]] = None,
        variogram_function: Optional[Callable[..., Any]] = None,
        nlags: int = 6,
        weight: bool = False,
        verbose: bool = False,
        enable_plotting: bool = False,
        exact_values: bool = True,
        pseudo_inv: bool = False,
        pseudo_inv_type: str = "pinv",
        backend: Backend = "vectorized",
        anisotropy_scaling: float | tuple[float, float] = 1.0,
        anisotropy_angle: float | tuple[float, float, float] = 0.0,
        coordinates_type: Literal["euclidean", "geographic"] = "euclidean",
    ) -> None:
        """Initialize an ordinary kriging interpolator.

        Parameters
        ----------
        variogram_model : {"linear", "power", "gaussian", "spherical", "exponential", "hole-effect", "custom"}, default="linear"
            Variogram model name forwarded to the selected PyKrige class.
        variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
            Variogram parameters. If ``None``, PyKrige infers them.
        variogram_function : callable or None, default=None
            Custom variogram function used only for ``variogram_model="custom"``.
        nlags : int, default=6
            Number of lag bins for variogram fitting.
        weight : bool, default=False
            Whether semivariances are weighted in variogram fitting.
        verbose : bool, default=False
            Whether PyKrige emits logs.
        enable_plotting : bool, default=False
            Whether PyKrige plots variogram fits.
        exact_values : bool, default=True
            Whether interpolation reproduces training values exactly.
        pseudo_inv : bool, default=False
            Whether to use pseudo-inverse for solving the kriging system.
        pseudo_inv_type : {"pinv", "pinvh"}, default="pinv"
            Pseudo-inverse implementation name.
        backend : {"vectorized", "loop", "C"}, default="vectorized"
            Execution backend used by PyKrige ``execute``.
        anisotropy_scaling : float or tuple[float, float], default=1.0
            2D uses a single scalar. 3D accepts one scalar or ``(scaling_y, scaling_z)``.
        anisotropy_angle : float or tuple[float, float, float], default=0.0
            2D uses a single scalar. 3D accepts one scalar or
            ``(angle_x, angle_y, angle_z)``.
        coordinates_type : {"euclidean", "geographic"}, default="euclidean"
            Coordinate interpretation for 2D ordinary kriging.

        Returns
        -------
        None
            Stores configuration for use at fit time.

        Raises
        ------
        ValueError
            If ``coordinates_type`` is invalid.
        """
        super().__init__(
            variogram_model=variogram_model,
            variogram_parameters=variogram_parameters,
            variogram_function=variogram_function,
            nlags=nlags,
            weight=weight,
            verbose=verbose,
            enable_plotting=enable_plotting,
            exact_values=exact_values,
            pseudo_inv=pseudo_inv,
            pseudo_inv_type=pseudo_inv_type,
            backend=backend,
        )

        if coordinates_type not in {"euclidean", "geographic"}:
            raise ValueError(
                f"`coordinates_type` must be 'euclidean' or 'geographic'. "
                f"Got {coordinates_type!r}."
            )

        self.anisotropy_scaling = anisotropy_scaling
        self.anisotropy_angle = anisotropy_angle
        self.coordinates_type = coordinates_type

    def _build_model(self, coordinates: np.ndarray, values: np.ndarray) -> Any:
        """Build the ordinary kriging backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, 2)`` or
            ``(n_samples, 3)``.
        values : numpy.ndarray
            Training values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            A fitted ``OrdinaryKriging`` or ``OrdinaryKriging3D`` instance.

        Raises
        ------
        RuntimeError
            If input dimensionality is not 2 or 3.
        """
        if coordinates.shape[1] == 2:
            x = coordinates[:, 0]
            y = coordinates[:, 1]

            return OrdinaryKriging(
                x=x,
                y=y,
                z=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling=float(self.anisotropy_scaling),
                anisotropy_angle=float(self.anisotropy_angle),
                verbose=self.verbose,
                enable_plotting=self.enable_plotting,
                exact_values=self.exact_values,
                pseudo_inv=self.pseudo_inv,
                pseudo_inv_type=self.pseudo_inv_type,
                coordinates_type=self.coordinates_type,
            )

        if coordinates.shape[1] == 3:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            scaling = self._normalize_3d_scaling(self.anisotropy_scaling)
            angles = self._normalize_3d_angles(self.anisotropy_angle)

            return OrdinaryKriging3D(
                x=x,
                y=y,
                z=z,
                val=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling_y=scaling[0],
                anisotropy_scaling_z=scaling[1],
                anisotropy_angle_x=angles[0],
                anisotropy_angle_y=angles[1],
                anisotropy_angle_z=angles[2],
                verbose=self.verbose,
                enable_plotting=self.enable_plotting,
                exact_values=self.exact_values,
                pseudo_inv=self.pseudo_inv,
                pseudo_inv_type=self.pseudo_inv_type,
            )

        raise RuntimeError(f"Unsupported dimension: {coordinates.shape[1]}")


class UniversalKrigingInterpolator(BasePyKrigeInterpolator):
    """Interpolate scalar values using universal kriging in 2D or 3D.

    Supports drift terms (regional, specified, functional) consistent with
    PyKrige's UniversalKriging/UniversalKriging3D implementations. For
    ``specified`` drift, supply drift arrays to ``predict``/``predict_with_variance``
    via ``specified_drift_arrays``.
    """

    def __init__(
        self,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: Optional[dict[str, Any] | Sequence[float]] = None,
        variogram_function: Optional[Callable[..., Any]] = None,
        nlags: int = 6,
        weight: bool = False,
        verbose: bool = False,
        enable_plotting: bool = False,
        exact_values: bool = True,
        pseudo_inv: bool = False,
        pseudo_inv_type: str = "pinv",
        backend: Backend = "vectorized",
        anisotropy_scaling: float | tuple[float, float] = 1.0,
        anisotropy_angle: float | tuple[float, float, float] = 0.0,
        drift_terms: Optional[Iterable[str]] = None,
        point_drift: Optional[Any] = None,
        external_drift: Optional[np.ndarray] = None,
        external_drift_x: Optional[np.ndarray] = None,
        external_drift_y: Optional[np.ndarray] = None,
        specified_drift: Optional[Sequence[np.ndarray]] = None,
        functional_drift: Optional[Sequence[Callable[..., Any]]] = None,
    ) -> None:
        """Initialize a universal kriging interpolator.

        Parameters
        ----------
        variogram_model : {"linear", "power", "gaussian", "spherical", "exponential", "hole-effect", "custom"}, default="linear"
            Variogram model name forwarded to the selected PyKrige class.
        variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
            Variogram parameters. If ``None``, PyKrige infers them.
        variogram_function : callable or None, default=None
            Custom variogram function used only for ``variogram_model="custom"``.
        nlags : int, default=6
            Number of lag bins for variogram fitting.
        weight : bool, default=False
            Whether semivariances are weighted in variogram fitting.
        verbose : bool, default=False
            Whether PyKrige emits logs.
        enable_plotting : bool, default=False
            Whether PyKrige plots variogram fits.
        exact_values : bool, default=True
            Whether interpolation reproduces training values exactly.
        pseudo_inv : bool, default=False
            Whether to use pseudo-inverse for solving the kriging system.
        pseudo_inv_type : {"pinv", "pinvh"}, default="pinv"
            Pseudo-inverse implementation name.
        backend : {"vectorized", "loop", "C"}, default="vectorized"
            Execution backend used by PyKrige ``execute``. ``"C"`` is rejected.
        anisotropy_scaling : float or tuple[float, float], default=1.0
            2D uses a single scalar. 3D accepts one scalar or ``(scaling_y, scaling_z)``.
        anisotropy_angle : float or tuple[float, float, float], default=0.0
            2D uses a single scalar. 3D accepts one scalar or
            ``(angle_x, angle_y, angle_z)``.
        drift_terms : Iterable[str] or None, default=None
            Drift terms enabled in universal kriging.
        point_drift : Any or None, default=None
            Point-log drift data for 2D universal kriging.
        external_drift : numpy.ndarray or None, default=None
            External drift raster for 2D universal kriging.
        external_drift_x : numpy.ndarray or None, default=None
            X-axis coordinates for ``external_drift``.
        external_drift_y : numpy.ndarray or None, default=None
            Y-axis coordinates for ``external_drift``.
        specified_drift : Sequence[numpy.ndarray] or None, default=None
            Per-sample drift arrays used when ``"specified"`` drift is active.
        functional_drift : Sequence[callable] or None, default=None
            Callable drift functions used when ``"functional"`` drift is active.

        Returns
        -------
        None
            Stores configuration and drift-related data.

        Raises
        ------
        ValueError
            If ``backend="C"`` is requested.
        """
        super().__init__(
            variogram_model=variogram_model,
            variogram_parameters=variogram_parameters,
            variogram_function=variogram_function,
            nlags=nlags,
            weight=weight,
            verbose=verbose,
            enable_plotting=enable_plotting,
            exact_values=exact_values,
            pseudo_inv=pseudo_inv,
            pseudo_inv_type=pseudo_inv_type,
            backend=backend,
        )

        if backend == "C":
            raise ValueError(
                "`backend='C'` is not supported for UniversalKriging in PyKrige. "
                "Use 'vectorized' or 'loop'."
            )

        self.anisotropy_scaling = anisotropy_scaling
        self.anisotropy_angle = anisotropy_angle

        self.drift_terms = None if drift_terms is None else list(drift_terms)
        self.point_drift = point_drift
        self.external_drift = external_drift
        self.external_drift_x = external_drift_x
        self.external_drift_y = external_drift_y
        self.specified_drift = specified_drift
        self.functional_drift = functional_drift

    def _fit_impl(self, coordinates: np.ndarray, values: np.ndarray) -> None:
        """Fit the universal kriging model with drift validation.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Training values with shape ``(n_samples,)``.

        Returns
        -------
        None
            This method stores the fitted backend model on the instance.
        """
        self._ensure_pykrige_installed()
        self._validate_universal_kriging_args(coordinates, values)

        self._fit_coordinates = np.asarray(coordinates, dtype=float)
        self._fit_values = np.asarray(values, dtype=float)
        self._model = self._build_model(self._fit_coordinates, self._fit_values)

    def predict(self, coordinates: np.ndarray, **execute_kwargs: Any) -> np.ndarray:
        """Predict values at query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_queries,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        predictions, _ = self._execute_points(coordinates, **execute_kwargs)
        return predictions

    def predict_variance(
        self,
        coordinates: np.ndarray,
        **execute_kwargs: Any,
    ) -> np.ndarray:
        """Predict kriging variance at query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        numpy.ndarray
            Variance values with shape ``(n_queries,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        _, variance = self._execute_points(coordinates, **execute_kwargs)
        return variance

    def predict_with_variance(
        self,
        coordinates: np.ndarray,
        **execute_kwargs: Any,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Predict values and variance at query coordinates.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige ``execute``.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Two arrays ``(prediction, variance)``, each shaped ``(n_queries,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)
        return self._execute_points(coordinates, **execute_kwargs)

    def _predict_impl(self, coordinates: np.ndarray) -> np.ndarray:
        """Internal point prediction implementation.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Query coordinates with shape ``(n_queries, n_dims)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_queries,)``.
        """
        predictions, _ = self._execute_points(coordinates)
        return predictions

    def _build_model(self, coordinates: np.ndarray, values: np.ndarray) -> Any:
        """Build the universal kriging backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, 2)`` or
            ``(n_samples, 3)``.
        values : numpy.ndarray
            Training values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            A fitted ``UniversalKriging`` or ``UniversalKriging3D`` instance.

        Raises
        ------
        RuntimeError
            If input dimensionality is not 2 or 3.
        """
        if coordinates.shape[1] == 2:
            x = coordinates[:, 0]
            y = coordinates[:, 1]

            return UniversalKriging(
                x=x,
                y=y,
                z=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling=float(self.anisotropy_scaling),
                anisotropy_angle=float(self.anisotropy_angle),
                drift_terms=self.drift_terms,
                point_drift=self.point_drift,
                external_drift=self.external_drift,
                external_drift_x=self.external_drift_x,
                external_drift_y=self.external_drift_y,
                specified_drift=self.specified_drift,
                functional_drift=self.functional_drift,
                verbose=self.verbose,
                enable_plotting=self.enable_plotting,
                exact_values=self.exact_values,
                pseudo_inv=self.pseudo_inv,
                pseudo_inv_type=self.pseudo_inv_type,
            )

        if coordinates.shape[1] == 3:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            scaling = self._normalize_3d_scaling(self.anisotropy_scaling)
            angles = self._normalize_3d_angles(self.anisotropy_angle)

            return UniversalKriging3D(
                x=x,
                y=y,
                z=z,
                val=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling_y=scaling[0],
                anisotropy_scaling_z=scaling[1],
                anisotropy_angle_x=angles[0],
                anisotropy_angle_y=angles[1],
                anisotropy_angle_z=angles[2],
                drift_terms=self.drift_terms,
                specified_drift=self.specified_drift,
                functional_drift=self.functional_drift,
                verbose=self.verbose,
                enable_plotting=self.enable_plotting,
                exact_values=self.exact_values,
                pseudo_inv=self.pseudo_inv,
                pseudo_inv_type=self.pseudo_inv_type,
            )

        raise RuntimeError(f"Unsupported dimension: {coordinates.shape[1]}")

    def _validate_universal_kriging_args(
        self,
        coordinates: np.ndarray,
        values: np.ndarray,
    ) -> None:
        """Validate universal-kriging drift-related inputs.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Training coordinates with shape ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Training values with shape ``(n_samples,)``.

        Returns
        -------
        None
            Raises on invalid drift configuration or incompatible inputs.
        """
        dim = int(coordinates.shape[1])
        n_samples = int(coordinates.shape[0])

        self._validate_drift_terms(dim)
        self._validate_point_drift(dim)
        self._validate_external_drift(dim)
        self._validate_specified_drift(n_samples)
        self._validate_functional_drift(dim)

    def _validate_drift_terms(self, dim: int) -> None:
        """Validate requested drift-term names for the current dimensionality.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality (2 or 3).

        Returns
        -------
        None
            Raises when drift-term names are invalid.
        """
        if self.drift_terms is None:
            return

        if not isinstance(self.drift_terms, (list, tuple)):
            raise TypeError("`drift_terms` must be a list or tuple of strings.")
        if len(self.drift_terms) == 0:
            raise ValueError("`drift_terms` cannot be empty when provided.")

        allowed_2d = {"regional_linear", "point_log", "external_Z", "specified", "functional"}
        allowed_3d = {"regional_linear", "specified", "functional"}
        allowed = allowed_2d if dim == 2 else allowed_3d

        for term in self.drift_terms:
            if not isinstance(term, str):
                raise TypeError(
                    f"Each entry in `drift_terms` must be a string. Got {type(term).__name__}."
                )
            if term not in allowed:
                raise ValueError(
                    f"Unsupported drift term {term!r} for dim={dim}. "
                    f"Allowed terms are {sorted(allowed)}."
                )

    def _validate_point_drift(self, dim: int) -> None:
        """Validate point-log drift input for 2D universal kriging.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality (2 or 3).

        Returns
        -------
        None
            Raises when point-drift data is malformed or incompatible.
        """
        if self.point_drift is None:
            return

        if dim != 2:
            raise ValueError("`point_drift` is supported only for 2D Universal Kriging.")

        if self.drift_terms is not None and "point_log" not in self.drift_terms:
            raise ValueError(
                "`point_drift` was provided, but `drift_terms` does not include 'point_log'."
            )

        arr = np.asarray(self.point_drift, dtype=float)

        if arr.ndim == 1:
            if arr.size == 0:
                raise ValueError("`point_drift` cannot be empty.")
            if arr.size % 3 != 0:
                raise ValueError(
                    "`point_drift` 1D form must contain triples [x, y, value, ...]."
                )
            if not np.isfinite(arr).all():
                raise ValueError("`point_drift` contains NaN or inf.")
            return

        if arr.ndim == 2:
            if arr.shape[0] == 0:
                raise ValueError("`point_drift` cannot be empty.")
            if arr.shape[1] != 3:
                raise ValueError(
                    "`point_drift` 2D form must have shape (n_points, 3) "
                    "with columns [x, y, value]."
                )
            if not np.isfinite(arr).all():
                raise ValueError("`point_drift` contains NaN or inf.")
            return

        raise ValueError(
            "`point_drift` must be either a 1D flat array or a 2D array "
            "of shape (n_points, 3)."
        )

    def _validate_external_drift(self, dim: int) -> None:
        """Validate external drift arrays for 2D universal kriging.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality (2 or 3).

        Returns
        -------
        None
            Raises when external drift arrays are inconsistent or invalid.
        """
        has_any_external = any(
            item is not None
            for item in (self.external_drift, self.external_drift_x, self.external_drift_y)
        )

        if not has_any_external:
            return

        if dim != 2:
            raise ValueError("External drift is supported only for 2D Universal Kriging.")

        if self.drift_terms is not None and "external_Z" not in self.drift_terms:
            raise ValueError(
                "External drift arrays were provided, but `drift_terms` "
                "does not include 'external_Z'."
            )

        all_present = (
            self.external_drift is not None
            and self.external_drift_x is not None
            and self.external_drift_y is not None
        )
        if not all_present:
            raise ValueError(
                "External drift requires all of `external_drift`, "
                "`external_drift_x`, and `external_drift_y`."
            )

        ext = np.asarray(self.external_drift, dtype=float)
        ext_x = np.asarray(self.external_drift_x, dtype=float)
        ext_y = np.asarray(self.external_drift_y, dtype=float)

        if ext.ndim != 2:
            raise ValueError("`external_drift` must be a 2D array.")
        if ext_x.ndim != 1:
            raise ValueError("`external_drift_x` must be a 1D array.")
        if ext_y.ndim != 1:
            raise ValueError("`external_drift_y` must be a 1D array.")

        if ext.shape != (ext_y.size, ext_x.size):
            raise ValueError(
                "`external_drift` shape must match "
                f"(len(external_drift_y), len(external_drift_x)). "
                f"Got {ext.shape} vs ({ext_y.size}, {ext_x.size})."
            )

        if ext_x.size < 2 or ext_y.size < 2:
            raise ValueError(
                "`external_drift_x` and `external_drift_y` must each contain "
                "at least 2 coordinates."
            )

        if not np.isfinite(ext).all():
            raise ValueError("`external_drift` contains NaN or inf.")
        if not np.isfinite(ext_x).all():
            raise ValueError("`external_drift_x` contains NaN or inf.")
        if not np.isfinite(ext_y).all():
            raise ValueError("`external_drift_y` contains NaN or inf.")

    def _validate_specified_drift(self, n_samples: int) -> None:
        """Validate per-sample specified drift arrays.

        Parameters
        ----------
        n_samples : int
            Number of training samples used for fitting.

        Returns
        -------
        None
            Raises when specified drift arrays have invalid shape or values.
        """
        if self.specified_drift is None:
            return

        if not isinstance(self.specified_drift, (list, tuple)):
            raise TypeError("`specified_drift` must be a list or tuple of arrays.")
        if len(self.specified_drift) == 0:
            raise ValueError("`specified_drift` cannot be empty when provided.")

        if self.drift_terms is not None and "specified" not in self.drift_terms:
            raise ValueError(
                "`specified_drift` was provided, but `drift_terms` does not include 'specified'."
            )

        for i, arr in enumerate(self.specified_drift):
            a = np.asarray(arr, dtype=float)

            if a.ndim != 1:
                raise ValueError(
                    f"`specified_drift[{i}]` must be 1D with one value per sample. "
                    f"Got shape {a.shape}."
                )
            if a.shape[0] != n_samples:
                raise ValueError(
                    f"`specified_drift[{i}]` length must match number of fitted samples "
                    f"({n_samples}). Got {a.shape[0]}."
                )
            if not np.isfinite(a).all():
                raise ValueError(f"`specified_drift[{i}]` contains NaN or inf.")

    def _validate_functional_drift(self, dim: int) -> None:
        """Validate functional drift callables.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality (2 or 3).

        Returns
        -------
        None
            Raises when drift functions are not callable or return invalid values.
        """
        if self.functional_drift is None:
            return

        if not isinstance(self.functional_drift, (list, tuple)):
            raise TypeError("`functional_drift` must be a list or tuple of callables.")
        if len(self.functional_drift) == 0:
            raise ValueError("`functional_drift` cannot be empty when provided.")

        if self.drift_terms is not None and "functional" not in self.drift_terms:
            raise ValueError(
                "`functional_drift` was provided, but `drift_terms` does not include 'functional'."
            )

        for i, fn in enumerate(self.functional_drift):
            if not callable(fn):
                raise TypeError(
                    f"`functional_drift[{i}]` must be callable. "
                    f"Got {type(fn).__name__}."
                )

            try:
                if dim == 2:
                    out = fn(np.array([0.0]), np.array([0.0]))
                elif dim == 3:
                    out = fn(np.array([0.0]), np.array([0.0]), np.array([0.0]))
                else:  # pragma: no cover
                    raise RuntimeError(f"Unsupported dim={dim}.")
            except Exception as e:
                raise ValueError(
                    f"`functional_drift[{i}]` could not be called with "
                    f"{dim}D coordinate arrays: {e}"
                ) from e

            out = np.asarray(out, dtype=float)
            if out.shape not in {(), (1,)}:
                raise ValueError(
                    f"`functional_drift[{i}]` must return a scalar or shape-(n,) array. "
                    f"Test call returned shape {out.shape}."
                )
            if not np.isfinite(out).all():
                raise ValueError(
                    f"`functional_drift[{i}]` returned NaN or inf in the validation call."
                )