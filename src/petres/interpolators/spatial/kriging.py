from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterable, Sequence
from typing import Any, Literal

import numpy as np
from numpy.typing import DTypeLike, NDArray
from pykrige.ok import OrdinaryKriging
from pykrige.ok3d import OrdinaryKriging3D
from pykrige.uk import UniversalKriging
from pykrige.uk3d import UniversalKriging3D

from ..base import BaseInterpolator


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

_ALLOWED_VARIOGRAM_MODELS = {
    "linear",
    "power",
    "gaussian",
    "spherical",
    "exponential",
    "hole-effect",
    "custom",
}

# Keyword arguments that this wrapper already supplies to PyKrige's
# ``execute`` method (positionally or via configuration). Allowing callers
# to also pass these through ``**execute_kwargs`` would raise a confusing
# "got multiple values for keyword argument" TypeError, so we reject them
# early with a clear message instead.
_RESERVED_EXECUTE_KWARGS = {
    "style",
    "xpoints",
    "ypoints",
    "zpoints",
    "backend",
}


def _is_scalar_like(value: Any) -> bool:
    """Return True if ``value`` behaves like a single scalar number.

    This is more robust than ``np.isscalar`` because it also treats 0-d
    numpy arrays (e.g. ``np.array(1.0)``) as scalars, which ``np.isscalar``
    does not.

    Parameters
    ----------
    value : Any
        Candidate value.

    Returns
    -------
    bool
        ``True`` if ``value`` is a Python/numpy scalar or a 0-d array.
    """
    if isinstance(value, (tuple, list)):
        return False
    return np.ndim(value) == 0


class BasePyKrigeInterpolator(BaseInterpolator):
    """Provide a common PyKrige-backed point interpolation API.

    This class adapts PyKrige model classes to the
    :class:`~.BaseInterpolator` contract.

    It centralizes:

    - common PyKrige configuration,
    - PyKrige-specific fit workflow,
    - point-based prediction,
    - prediction variance,
    - combined prediction and variance.

    Subclasses only need to implement :meth:`_build_model` and may
    override :meth:`_validate_fit_specific_args` when additional
    fit-time validation is required.

    Parameters
    ----------
    variogram_model : {"linear", "power", "gaussian", "spherical",
            "exponential", "hole-effect", "custom"}, default="linear"
        Variogram model name forwarded to the PyKrige backend model.
    variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
        Explicit variogram parameters. If ``None``, PyKrige estimates the
        parameters from input data.
    variogram_function : callable or None, default=None
        Custom variogram function used when ``variogram_model="custom"``.
    nlags : int, default=6
        Number of lag bins used for variogram estimation. Must be at least 1.
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

    Notes
    -----
    Only point prediction mode is supported. Grid-style execution is
    intentionally omitted to keep the API aligned with point-based
    workflows.

    ``BaseInterpolator`` is responsible for validating interpolation
    coordinates and values. This class therefore assumes that arguments
    received by :meth:`_fit_impl` and :meth:`_predict_impl` have already
    passed the generic validation performed by the base class.
    """

    allowed_dims = (2, 3)

    def __init__(
        self,
        *,
        dtype: DTypeLike = np.float64,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: dict[str, Any] | Sequence[float] | None = None,
        variogram_function: Callable[..., Any] | None = None,
        nlags: int = 6,
        weight: bool = False,
        verbose: bool = False,
        enable_plotting: bool = False,
        exact_values: bool = True,
        pseudo_inv: bool = False,
        pseudo_inv_type: str = "pinv",
        backend: Backend = "vectorized",
    ) -> None:
        """Initialize shared PyKrige options.

        Raises
        ------
        ValueError
            If ``nlags < 1``, ``variogram_model`` is unsupported (and not a
            custom callable case), ``pseudo_inv_type`` is unsupported, or
            ``backend`` is not one of the accepted values.
        """
        super().__init__(dtype=dtype)

        if nlags < 1:
            raise ValueError(f"`nlags` must be >= 1. Got {nlags}.")

        if variogram_model not in _ALLOWED_VARIOGRAM_MODELS:
            raise ValueError(
                "`variogram_model` must be one of "
                f"{sorted(_ALLOWED_VARIOGRAM_MODELS)}. Got {variogram_model!r}."
            )

        if variogram_model == "custom" and variogram_function is None:
            raise ValueError(
                "`variogram_function` must be provided when "
                "`variogram_model='custom'`."
            )

        if pseudo_inv_type not in {"pinv", "pinvh"}:
            raise ValueError(
                "`pseudo_inv_type` must be 'pinv' or 'pinvh'. "
                f"Got {pseudo_inv_type!r}."
            )

        if backend not in {"vectorized", "loop", "C"}:
            raise ValueError(
                "`backend` must be 'vectorized', 'loop', or 'C'. "
                f"Got {backend!r}."
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

    # ------------------------------------------------------------------
    # BaseInterpolator hooks
    # ------------------------------------------------------------------

    def _fit_impl(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> None:
        """Fit the wrapped PyKrige model.

        Generic coordinate/value validation has already been performed
        by :class:`BaseInterpolator`.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates with shape
            ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Validated training values with shape ``(n_samples,)``.
        """
        self._validate_fit_specific_args(coordinates)

        self._model = self._build_model(coordinates, values)

    def _predict_impl(
        self,
        coordinates: NDArray[Any],
    ) -> NDArray[Any]:
        """Predict values using the fitted PyKrige model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated query coordinates with shape
            ``(n_queries, n_dims)``.

        Returns
        -------
        numpy.ndarray
            Predicted values with shape ``(n_queries,)``.
        """
        predictions, _ = self._execute_points(coordinates)
        return predictions

    def _validate_fit_specific_args(
        self,
        coordinates: NDArray[Any],
    ) -> None:
        """Validate subclass-specific fit arguments.

        This hook is intentionally empty in the common PyKrige base class.

        Subclasses can override it when their configuration depends on
        the dimensionality or number of fitted samples.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates.
        """
        return

    # ------------------------------------------------------------------
    # Public PyKrige prediction API
    # ------------------------------------------------------------------

    def predict(
        self,
        coordinates: NDArray[Any],
        **execute_kwargs: Any,
    ) -> NDArray[Any]:
        """Predict interpolated values at new coordinates.

        This method extends :meth:`BaseInterpolator.predict` with
        additional keyword arguments forwarded to PyKrige's
        ``execute`` method.

        Parameters
        ----------
        coordinates : ArrayLike
            Coordinates with shape ``(n_points, dim)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige
            ``execute``. Must not include ``style``, ``xpoints``,
            ``ypoints``, ``zpoints``, or ``backend``, which are already
            supplied internally.

        Returns
        -------
        numpy.ndarray
            Predicted values with one value per input coordinate.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)

        predictions, _ = self._execute_points(
            coordinates,
            **execute_kwargs,
        )

        return predictions

    def predict_variance(
        self,
        coordinates: NDArray[Any],
        **execute_kwargs: Any,
    ) -> NDArray[Any]:
        """Predict kriging variance for query coordinates.

        Parameters
        ----------
        coordinates : ArrayLike
            Coordinates with shape ``(n_points, dim)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige
            ``execute``. Must not include ``style``, ``xpoints``,
            ``ypoints``, ``zpoints``, or ``backend``, which are already
            supplied internally.

        Returns
        -------
        numpy.ndarray
            Kriging variance values with shape ``(n_points,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)

        _, variance = self._execute_points(
            coordinates,
            **execute_kwargs,
        )

        return variance

    def predict_with_variance(
        self,
        coordinates: NDArray[Any],
        **execute_kwargs: Any,
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        """Predict values and kriging variance.

        Parameters
        ----------
        coordinates : ArrayLike
            Coordinates with shape ``(n_points, dim)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige
            ``execute``. Must not include ``style``, ``xpoints``,
            ``ypoints``, ``zpoints``, or ``backend``, which are already
            supplied internally.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Prediction and variance arrays, each with shape
            ``(n_points,)``.
        """
        self._check_fitted()
        coordinates = self._validate_predict_inputs(coordinates)

        return self._execute_points(
            coordinates,
            **execute_kwargs,
        )

    # ------------------------------------------------------------------
    # PyKrige execution
    # ------------------------------------------------------------------

    def _execute_points(
        self,
        coordinates: NDArray[Any],
        **execute_kwargs: Any,
    ) -> tuple[NDArray[Any], NDArray[Any]]:
        """Execute point-based kriging on the backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated query coordinates with shape
            ``(n_queries, n_dims)``.
        **execute_kwargs : Any
            Additional keyword arguments forwarded to PyKrige
            ``execute``.

        Returns
        -------
        tuple[numpy.ndarray, numpy.ndarray]
            Prediction and variance arrays with shape ``(n_queries,)``.

        Raises
        ------
        RuntimeError
            If the backend model is missing or the fitted dimensionality
            is unsupported.
        ValueError
            If ``execute_kwargs`` contains a key that this wrapper
            already supplies internally (e.g. ``backend`` or ``style``).
        """
        if self._model is None:
            raise RuntimeError(
                "Interpolator missing fitted PyKrige model "
                "(internal error)."
            )

        clashing = _RESERVED_EXECUTE_KWARGS & execute_kwargs.keys()
        if clashing:
            raise ValueError(
                "The following `execute_kwargs` are already supplied "
                f"internally and cannot be overridden: {sorted(clashing)}."
            )

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
            raise RuntimeError(
                f"Unsupported fitted dim_: {self.dim_}"
            )

        return (
            np.asarray(pred, dtype=float).ravel(),
            np.asarray(var, dtype=float).ravel(),
        )

    # ------------------------------------------------------------------
    # Backend construction
    # ------------------------------------------------------------------

    @abstractmethod
    def _build_model(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> Any:
        """Build and return a fitted backend kriging model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates with shape
            ``(n_samples, n_dims)``.
        values : numpy.ndarray
            Validated training values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            Backend-specific fitted kriging model instance.
        """
        ...

    # ------------------------------------------------------------------
    # Shared anisotropy normalization
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_2d_scalar(
        value: float,
        name: str,
    ) -> float:
        """Normalize a 2D anisotropy scalar parameter.

        Parameters
        ----------
        value : float
            User-provided scalar (e.g. ``anisotropy_scaling`` or
            ``anisotropy_angle`` for 2D kriging).
        name : str
            Parameter name, used in error messages.

        Returns
        -------
        float
            The value converted to ``float``.

        Raises
        ------
        ValueError
            If ``value`` is not scalar-like (e.g. a tuple/list/array
            with more than one element), or cannot be converted to
            ``float``.
        """
        if not _is_scalar_like(value):
            raise ValueError(
                f"`{name}` for 2D kriging must be a single float. "
                f"Got {type(value).__name__}: {value!r}. "
                "Tuple values are only supported for 3D kriging."
            )

        try:
            return float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"`{name}` must be convertible to float. Got {value!r}."
            ) from exc

    @staticmethod
    def _normalize_3d_scaling(
        value: float | tuple[float, float],
    ) -> tuple[float, float]:
        """Normalize 3D anisotropy scaling.

        Parameters
        ----------
        value : float or tuple[float, float]
            User-provided scaling. A scalar is applied to both axes.

        Returns
        -------
        tuple[float, float]
            Scaling factors ``(scaling_y, scaling_z)``.

        Raises
        ------
        ValueError
            If tuple input does not have length 2.
        """
        if _is_scalar_like(value):
            v = float(value)
            return v, v

        if len(value) != 2:
            raise ValueError(
                "`anisotropy_scaling` for 3D must be a float or "
                "a tuple of length 2 (scaling_y, scaling_z)."
            )

        return float(value[0]), float(value[1])

    @staticmethod
    def _normalize_3d_angles(
        value: float | tuple[float, float, float],
    ) -> tuple[float, float, float]:
        """Normalize 3D anisotropy rotation angles.

        Parameters
        ----------
        value : float or tuple[float, float, float]
            User-provided rotation angle. A scalar is applied to all axes.

        Returns
        -------
        tuple[float, float, float]
            Rotation angles ``(angle_x, angle_y, angle_z)``.

        Raises
        ------
        ValueError
            If tuple input does not have length 3.
        """
        if _is_scalar_like(value):
            v = float(value)
            return v, v, v

        if len(value) != 3:
            raise ValueError(
                "`anisotropy_angle` for 3D must be a float or "
                "a tuple of length 3 "
                "(angle_x, angle_y, angle_z)."
            )

        return (
            float(value[0]),
            float(value[1]),
            float(value[2]),
        )


class OrdinaryKrigingInterpolator(BasePyKrigeInterpolator):
    """Interpolate scalar values using ordinary kriging in 2D or 3D.

    The implementation selects ``OrdinaryKriging`` for 2D coordinates
    and ``OrdinaryKriging3D`` for 3D coordinates.

    Parameters
    ----------
    variogram_model : {"linear", "power", "gaussian", "spherical",
            "exponential", "hole-effect", "custom"}, default="linear"
        Variogram model name forwarded to PyKrige.
    variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
        Explicit variogram parameters.
    variogram_function : callable or None, default=None
        Custom variogram function.
    nlags : int, default=6
        Number of lag bins.
    weight : bool, default=False
        Whether semivariances are weighted during fitting.
    verbose : bool, default=False
        Whether PyKrige emits logs.
    enable_plotting : bool, default=False
        Whether PyKrige variogram plots are enabled.
    exact_values : bool, default=True
        Whether interpolation reproduces training values exactly.
    pseudo_inv : bool, default=False
        Whether to use a pseudo-inverse.
    pseudo_inv_type : {"pinv", "pinvh"}, default="pinv"
        Pseudo-inverse implementation.
    backend : {"vectorized", "loop", "C"}, default="vectorized"
        PyKrige execution backend.
    anisotropy_scaling : float or tuple[float, float], default=1.0
        2D uses a scalar. 3D accepts a scalar or
        ``(scaling_y, scaling_z)``.
    anisotropy_angle : float or tuple[float, float, float], default=0.0
        2D uses a scalar. 3D accepts a scalar or
        ``(angle_x, angle_y, angle_z)``.
    coordinates_type : {"euclidean", "geographic"}, default="euclidean"
        Coordinate interpretation for 2D ordinary kriging. Only valid
        when the interpolator is fitted with 2D coordinates.
    """

    def __init__(
        self,
        *,
        dtype: DTypeLike = np.float64,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: dict[str, Any] | Sequence[float] | None = None,
        variogram_function: Callable[..., Any] | None = None,
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
        coordinates_type: Literal[
            "euclidean",
            "geographic",
        ] = "euclidean",
    ) -> None:
        """Initialize an ordinary kriging interpolator.

        Raises
        ------
        ValueError
            If ``coordinates_type`` is invalid.
        """
        super().__init__(
            dtype=dtype,
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
                "`coordinates_type` must be 'euclidean' or 'geographic'. "
                f"Got {coordinates_type!r}."
            )

        self.anisotropy_scaling = anisotropy_scaling
        self.anisotropy_angle = anisotropy_angle
        self.coordinates_type = coordinates_type

    def _validate_fit_specific_args(
        self,
        coordinates: NDArray[Any],
    ) -> None:
        """Validate ordinary-kriging-specific fit arguments.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates.

        Raises
        ------
        ValueError
            If ``coordinates_type='geographic'`` is combined with 3D
            coordinates, which PyKrige's ``OrdinaryKriging3D`` does not
            support (the option would otherwise be silently ignored).
        """
        dim = int(coordinates.shape[1])

        if dim == 3 and self.coordinates_type != "euclidean":
            raise ValueError(
                "`coordinates_type='geographic'` is only supported for "
                "2D Ordinary Kriging. 3D Ordinary Kriging "
                "(OrdinaryKriging3D) has no geographic coordinate mode; "
                "leaving this unchecked would cause the option to be "
                "silently ignored."
            )

    def _build_model(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> Any:
        """Build the ordinary kriging backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated coordinates with shape ``(n_samples, 2)`` or
            ``(n_samples, 3)``.
        values : numpy.ndarray
            Validated values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            A fitted ``OrdinaryKriging`` or ``OrdinaryKriging3D`` instance.
        """
        dim = coordinates.shape[1]

        if dim == 2:
            x = coordinates[:, 0]
            y = coordinates[:, 1]

            scaling = self._normalize_2d_scalar(
                self.anisotropy_scaling, "anisotropy_scaling"
            )
            angle = self._normalize_2d_scalar(
                self.anisotropy_angle, "anisotropy_angle"
            )

            return OrdinaryKriging(
                x=x,
                y=y,
                z=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling=scaling,
                anisotropy_angle=angle,
                verbose=self.verbose,
                enable_plotting=self.enable_plotting,
                exact_values=self.exact_values,
                pseudo_inv=self.pseudo_inv,
                pseudo_inv_type=self.pseudo_inv_type,
                coordinates_type=self.coordinates_type,
            )

        if dim == 3:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            scaling = self._normalize_3d_scaling(
                self.anisotropy_scaling
            )
            angles = self._normalize_3d_angles(
                self.anisotropy_angle
            )

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

        # This should be unreachable because BaseInterpolator validates
        # against allowed_dims = (2, 3).
        raise RuntimeError(f"Unsupported dimension: {dim}")  # pragma: no cover


class UniversalKrigingInterpolator(BasePyKrigeInterpolator):
    """Interpolate scalar values using universal kriging in 2D or 3D.

    Supports drift terms consistent with PyKrige's
    ``UniversalKriging`` and ``UniversalKriging3D`` implementations.

    Parameters
    ----------
    variogram_model : {"linear", "power", "gaussian", "spherical",
            "exponential", "hole-effect", "custom"}, default="linear"
        Variogram model name forwarded to PyKrige.
    variogram_parameters : dict[str, Any] or Sequence[float] or None, default=None
        Explicit variogram parameters.
    variogram_function : callable or None, default=None
        Custom variogram function.
    nlags : int, default=6
        Number of lag bins.
    weight : bool, default=False
        Whether semivariances are weighted during fitting.
    verbose : bool, default=False
        Whether PyKrige emits logs.
    enable_plotting : bool, default=False
        Whether PyKrige variogram plots are enabled.
    exact_values : bool, default=True
        Whether interpolation reproduces training values exactly.
    pseudo_inv : bool, default=False
        Whether to use a pseudo-inverse.
    pseudo_inv_type : {"pinv", "pinvh"}, default="pinv"
        Pseudo-inverse implementation.
    backend : {"vectorized", "loop"}, default="vectorized"
        PyKrige execution backend. ``"C"`` is not supported for
        Universal Kriging.
    anisotropy_scaling : float or tuple[float, float], default=1.0
        2D uses a scalar. 3D accepts a scalar or
        ``(scaling_y, scaling_z)``.
    anisotropy_angle : float or tuple[float, float, float], default=0.0
        2D uses a scalar. 3D accepts a scalar or
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
        Per-sample drift arrays used with ``"specified"`` drift.
    functional_drift : Sequence[callable] or None, default=None
        Callable drift functions used with ``"functional"`` drift.
    """

    def __init__(
        self,
        *,
        dtype: DTypeLike = np.float64,
        variogram_model: VariogramModel = "linear",
        variogram_parameters: dict[str, Any] | Sequence[float] | None = None,
        variogram_function: Callable[..., Any] | None = None,
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
        drift_terms: Iterable[str] | None = None,
        point_drift: Any | None = None,
        external_drift: np.ndarray | None = None,
        external_drift_x: np.ndarray | None = None,
        external_drift_y: np.ndarray | None = None,
        specified_drift: Sequence[np.ndarray] | None = None,
        functional_drift: Sequence[Callable[..., Any]] | None = None,
    ) -> None:
        """Initialize a universal kriging interpolator.

        Raises
        ------
        ValueError
            If ``backend="C"`` is requested.
        """
        super().__init__(
            dtype=dtype,
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
                "`backend='C'` is not supported for UniversalKriging "
                "in PyKrige. Use 'vectorized' or 'loop'."
            )

        self.anisotropy_scaling = anisotropy_scaling
        self.anisotropy_angle = anisotropy_angle

        self.drift_terms = (
            None
            if drift_terms is None
            else list(drift_terms)
        )

        self.point_drift = point_drift
        self.external_drift = external_drift
        self.external_drift_x = external_drift_x
        self.external_drift_y = external_drift_y
        self.specified_drift = specified_drift
        self.functional_drift = functional_drift

    # ------------------------------------------------------------------
    # Universal-Kriging-specific validation
    # ------------------------------------------------------------------

    def _validate_fit_specific_args(
        self,
        coordinates: NDArray[Any],
    ) -> None:
        """Validate universal-kriging-specific fit arguments.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates.
        """
        self._validate_universal_kriging_args(coordinates)

    def _validate_universal_kriging_args(
        self,
        coordinates: NDArray[Any],
    ) -> None:
        """Validate drift-related universal-kriging arguments.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated training coordinates.
        """
        dim = int(coordinates.shape[1])
        n_samples = int(coordinates.shape[0])

        self._validate_drift_terms(dim)
        self._validate_point_drift(dim)
        self._validate_external_drift(dim)
        self._validate_specified_drift(n_samples)
        self._validate_functional_drift(dim)

    def _validate_drift_terms(self, dim: int) -> None:
        """Validate requested drift terms.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality.
        """
        if self.drift_terms is None:
            return

        if len(self.drift_terms) == 0:
            raise ValueError(
                "`drift_terms` cannot be empty when provided."
            )

        allowed_2d = {
            "regional_linear",
            "point_log",
            "external_Z",
            "specified",
            "functional",
        }

        allowed_3d = {
            "regional_linear",
            "specified",
            "functional",
        }

        allowed = (
            allowed_2d
            if dim == 2
            else allowed_3d
        )

        for term in self.drift_terms:
            if not isinstance(term, str):
                raise TypeError(
                    "Each entry in `drift_terms` must be a string. "
                    f"Got {type(term).__name__}."
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
            Interpolation dimensionality.
        """
        if self.point_drift is None:
            return

        if dim != 2:
            raise ValueError(
                "`point_drift` is supported only for 2D "
                "Universal Kriging."
            )

        if (
            self.drift_terms is not None
            and "point_log" not in self.drift_terms
        ):
            raise ValueError(
                "`point_drift` was provided, but `drift_terms` "
                "does not include 'point_log'."
            )

        arr = np.asarray(
            self.point_drift,
            dtype=float,
        )

        if arr.ndim == 1:
            if arr.size == 0:
                raise ValueError(
                    "`point_drift` cannot be empty."
                )

            if arr.size % 3 != 0:
                raise ValueError(
                    "`point_drift` 1D form must contain triples "
                    "[x, y, value, ...]."
                )

            if not np.isfinite(arr).all():
                raise ValueError(
                    "`point_drift` contains NaN or inf."
                )

            return

        if arr.ndim == 2:
            if arr.shape[0] == 0:
                raise ValueError(
                    "`point_drift` cannot be empty."
                )

            if arr.shape[1] != 3:
                raise ValueError(
                    "`point_drift` 2D form must have shape "
                    "(n_points, 3) with columns [x, y, value]."
                )

            if not np.isfinite(arr).all():
                raise ValueError(
                    "`point_drift` contains NaN or inf."
                )

            return

        raise ValueError(
            "`point_drift` must be either a 1D flat array or "
            "a 2D array of shape (n_points, 3)."
        )

    def _validate_external_drift(self, dim: int) -> None:
        """Validate external drift arrays for 2D universal kriging.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality.
        """
        has_any_external = any(
            item is not None
            for item in (
                self.external_drift,
                self.external_drift_x,
                self.external_drift_y,
            )
        )

        if not has_any_external:
            return

        if dim != 2:
            raise ValueError(
                "External drift is supported only for 2D "
                "Universal Kriging."
            )

        if (
            self.drift_terms is not None
            and "external_Z" not in self.drift_terms
        ):
            raise ValueError(
                "External drift arrays were provided, but "
                "`drift_terms` does not include 'external_Z'."
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

        ext = np.asarray(
            self.external_drift,
            dtype=float,
        )
        ext_x = np.asarray(
            self.external_drift_x,
            dtype=float,
        )
        ext_y = np.asarray(
            self.external_drift_y,
            dtype=float,
        )

        if ext.ndim != 2:
            raise ValueError(
                "`external_drift` must be a 2D array."
            )

        if ext_x.ndim != 1:
            raise ValueError(
                "`external_drift_x` must be a 1D array."
            )

        if ext_y.ndim != 1:
            raise ValueError(
                "`external_drift_y` must be a 1D array."
            )

        if ext.shape != (ext_y.size, ext_x.size):
            raise ValueError(
                "`external_drift` shape must match "
                "(len(external_drift_y), len(external_drift_x)). "
                f"Got {ext.shape} vs "
                f"({ext_y.size}, {ext_x.size})."
            )

        if ext_x.size < 2 or ext_y.size < 2:
            raise ValueError(
                "`external_drift_x` and `external_drift_y` must "
                "each contain at least 2 coordinates."
            )

        if not np.isfinite(ext).all():
            raise ValueError(
                "`external_drift` contains NaN or inf."
            )

        if not np.isfinite(ext_x).all():
            raise ValueError(
                "`external_drift_x` contains NaN or inf."
            )

        if not np.isfinite(ext_y).all():
            raise ValueError(
                "`external_drift_y` contains NaN or inf."
            )

    def _validate_specified_drift(
        self,
        n_samples: int,
    ) -> None:
        """Validate per-sample specified drift arrays.

        Parameters
        ----------
        n_samples : int
            Number of fitted samples.
        """
        if self.specified_drift is None:
            return

        if not isinstance(
            self.specified_drift,
            (list, tuple),
        ):
            raise TypeError(
                "`specified_drift` must be a list or tuple of arrays."
            )

        if len(self.specified_drift) == 0:
            raise ValueError(
                "`specified_drift` cannot be empty when provided."
            )

        if (
            self.drift_terms is not None
            and "specified" not in self.drift_terms
        ):
            raise ValueError(
                "`specified_drift` was provided, but `drift_terms` "
                "does not include 'specified'."
            )

        for i, arr in enumerate(self.specified_drift):
            a = np.asarray(
                arr,
                dtype=float,
            )

            if a.ndim != 1:
                raise ValueError(
                    f"`specified_drift[{i}]` must be 1D with one "
                    f"value per sample. Got shape {a.shape}."
                )

            if a.shape[0] != n_samples:
                raise ValueError(
                    f"`specified_drift[{i}]` length must match "
                    f"number of fitted samples ({n_samples}). "
                    f"Got {a.shape[0]}."
                )

            if not np.isfinite(a).all():
                raise ValueError(
                    f"`specified_drift[{i}]` contains NaN or inf."
                )

    def _validate_functional_drift(self, dim: int) -> None:
        """Validate functional drift callables.

        Each callable is smoke-tested with dummy 2-element coordinate
        arrays (rather than length-1 arrays) so that broadcasting bugs
        which only surface with more than one point are more likely to
        be caught here instead of during a later, harder-to-debug
        PyKrige call.

        Parameters
        ----------
        dim : int
            Interpolation dimensionality.
        """
        if self.functional_drift is None:
            return

        if not isinstance(
            self.functional_drift,
            (list, tuple),
        ):
            raise TypeError(
                "`functional_drift` must be a list or tuple "
                "of callables."
            )

        if len(self.functional_drift) == 0:
            raise ValueError(
                "`functional_drift` cannot be empty when provided."
            )

        if (
            self.drift_terms is not None
            and "functional" not in self.drift_terms
        ):
            raise ValueError(
                "`functional_drift` was provided, but `drift_terms` "
                "does not include 'functional'."
            )

        dummy = np.array([0.0, 1.0])

        for i, fn in enumerate(self.functional_drift):
            if not callable(fn):
                raise TypeError(
                    f"`functional_drift[{i}]` must be callable. "
                    f"Got {type(fn).__name__}."
                )

            try:
                if dim == 2:
                    out = fn(dummy, dummy)
                elif dim == 3:
                    out = fn(dummy, dummy, dummy)
                else:  # pragma: no cover
                    raise RuntimeError(
                        f"Unsupported dim={dim}."
                    )
            except Exception as exc:
                raise ValueError(
                    f"`functional_drift[{i}]` could not be called "
                    f"with {dim}D coordinate arrays: {exc}"
                ) from exc

            out = np.asarray(
                out,
                dtype=float,
            )

            if out.shape not in {(), (1,), (2,)}:
                raise ValueError(
                    f"`functional_drift[{i}]` must return a scalar "
                    f"or an array broadcastable to the input "
                    f"coordinates. Test call with 2 points returned "
                    f"shape {out.shape}."
                )

            if not np.isfinite(out).all():
                raise ValueError(
                    f"`functional_drift[{i}]` returned NaN or inf "
                    "in the validation call."
                )

    # ------------------------------------------------------------------
    # Backend construction
    # ------------------------------------------------------------------

    def _build_model(
        self,
        coordinates: NDArray[Any],
        values: NDArray[Any],
    ) -> Any:
        """Build the universal kriging backend model.

        Parameters
        ----------
        coordinates : numpy.ndarray
            Validated coordinates with shape ``(n_samples, 2)`` or
            ``(n_samples, 3)``.
        values : numpy.ndarray
            Validated values with shape ``(n_samples,)``.

        Returns
        -------
        Any
            A fitted ``UniversalKriging`` or ``UniversalKriging3D``
            instance.
        """
        dim = coordinates.shape[1]

        if dim == 2:
            x = coordinates[:, 0]
            y = coordinates[:, 1]

            scaling = self._normalize_2d_scalar(
                self.anisotropy_scaling, "anisotropy_scaling"
            )
            angle = self._normalize_2d_scalar(
                self.anisotropy_angle, "anisotropy_angle"
            )

            return UniversalKriging(
                x=x,
                y=y,
                z=values,
                variogram_model=self.variogram_model,
                variogram_parameters=self.variogram_parameters,
                variogram_function=self.variogram_function,
                nlags=self.nlags,
                weight=self.weight,
                anisotropy_scaling=scaling,
                anisotropy_angle=angle,
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

        if dim == 3:
            x = coordinates[:, 0]
            y = coordinates[:, 1]
            z = coordinates[:, 2]

            scaling = self._normalize_3d_scaling(
                self.anisotropy_scaling
            )
            angles = self._normalize_3d_angles(
                self.anisotropy_angle
            )

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

        # This should be unreachable because BaseInterpolator validates
        # against allowed_dims = (2, 3).
        raise RuntimeError(f"Unsupported dimension: {dim}")  # pragma: no cover