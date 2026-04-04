from __future__ import annotations

from collections.abc import Callable, ItemsView, Sequence, ValuesView
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal
import warnings
import numpy as np
from numpy.typing import ArrayLike


from .._validation import _validate_nonempty_string
from ..interpolators.base import BaseInterpolator
from ..errors.property import ExistingPropertyNameError, MissingEclipseKeywordError, MissingPropertyValueError, ReservedPropertyNameError
from ..errors.eclipse import GRDECLMissingValueError
from ..eclipse.grids.write import GRDECLWriter
from ..models.wells import VerticalWell
from ..models.zone import Zone

if TYPE_CHECKING:
    from .cornerpoint import CornerPointGrid


@dataclass
class GridProperty:
    """Represent a cell-based property defined on a corner-point grid.

    The property stores values per cell with shape ``(nk, nj, ni)`` and
    provides assignment helpers for constants, random distributions, functions,
    arrays, and well-based interpolation.

    Parameters
    ----------
    name : str
        Property name (must be unique on the grid).
    grid : CornerPointGrid
        Owning grid; used for shape and masking.
    values : ndarray or None, optional, default None
        Property values of shape ``(nk, nj, ni)``. If ``None``, initialized to
        NaN.
    eclipse_keyword : str or None, optional, default None
        Optional Eclipse keyword for export.
    description : str or None, optional, default None
        Free-form description.

    Notes
    -----
    Initialization delegates validation and normalization to
    :meth:`__post_init__`.
    """
    name: str = field(repr=True)
    grid: "CornerPointGrid" = field(repr=False)
    values: np.ndarray | None = None
    eclipse_keyword: str | None = None                 # Eclipse keyword (PORO, PERMX, ...)
    description: str | None = None

    def __init__(
        self,
        name: str,
        grid: "CornerPointGrid",
        values: ArrayLike | None = None,
        eclipse_keyword: str | None = None,
        description: str | None = None,
    ) -> None:
        """Initialize the property and run post-initialization validation.

        Raises
        ------
        TypeError
            If ``name`` or ``eclipse_keyword`` has an invalid type.
        ValueError
            If ``name`` is empty, ``values`` shape mismatches the grid, or
            ``eclipse_keyword`` resolves to an empty keyword.
        """
        self.name = name
        self.grid = grid
        self.values = None if values is None else np.asarray(values)
        self.eclipse_keyword = eclipse_keyword
        self.description = description
        self.__post_init__()

    def __post_init__(self) -> None:
        """Validate and normalize property initialization inputs.

        Raises
        ------
        TypeError
            If ``name`` is not a string or ``eclipse_keyword`` has invalid type.
        ValueError
            If ``name`` is empty, ``values`` shape mismatches grid shape, or
            ``eclipse_keyword`` resolves to an empty keyword.
        """
        if not isinstance(self.name, str):
            raise TypeError(f"`name` must be str, got {type(self.name)}.")
        
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("`name` cannot be empty.")

        if self.values is None:
            self.values = np.full(self.grid.shape, np.nan, dtype=float)
        else:
            self.values = np.asarray(self.values)

            if self.values.shape != self.grid.shape:
                raise ValueError(
                    f"`values` must match grid shape {self.grid.shape}, got {self.values.shape}."
                )

        if self.eclipse_keyword is not None:
            if not isinstance(self.eclipse_keyword, str):
                raise TypeError("`eclipse_keyword` must be a string or None.")
            keyword = GRDECLWriter._normalize_keyword(self.eclipse_keyword)
            if not keyword:
                raise ValueError("`eclipse_keyword` cannot be empty.")
            self.eclipse_keyword = keyword

        if self.name is not None:
            if not isinstance(self.name, str):
                raise TypeError("`name` must be a string or None.")
            if not self.name.strip():
                raise ValueError("`name` cannot be empty.")

    def show(
        self,
        *, 
        show_inactive: bool = False, 
        cmap: str | None = "turbo",
        title: str | Literal["auto"] | None = "auto", 
        **kwargs: Any
    ) -> None:
        """Visualize the property in 3D using the grid viewer.

        Parameters
        ----------
        show_inactive : bool, default False
            Whether to display inactive cells.
        cmap : str or None, default 'turbo'
            Colormap used for rendering.
        title : str or 'auto', default 'auto'
            Window title; ``'auto'`` uses the property name.
        **kwargs
            Forwarded to viewer ``add_grid``.

        Notes
        -----
        ``title='auto'`` expands to ``Property: <name>``.
        """
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_grid(grid=self.grid, show_inactive=show_inactive, scalars=self.values, cmap=cmap, **kwargs)
        if title == 'auto':
            title = f"Property: {self.name}"
        viewer.show(title=title)
                          
    @property
    def shape(self) -> tuple[int, int, int]:
        """Return property array shape.

        Returns
        -------
        tuple of int
            Shape ordered as ``(nk, nj, ni)``.
        """
        return self.values.shape

    @property
    def nk(self) -> int:
        """Return number of cells in k direction.

        Returns
        -------
        int
            Number of layers.
        """
        return self.shape[0]

    @property
    def nj(self) -> int:
        """Return number of cells in j direction.

        Returns
        -------
        int
            Number of rows.
        """
        return self.shape[1]
    
    @property
    def ni(self) -> int:
        """Return number of cells in i direction.

        Returns
        -------
        int
            Number of columns.
        """
        return self.shape[2]
    
    @property
    def n_cells(self) -> int:
        """Return total number of cells.

        Returns
        -------
        int
            Product ``nk * nj * ni``.
        """
        return self.nk * self.nj * self.ni

    @property
    def min(self) -> float:
        """Return minimum finite property value.

        Returns
        -------
        float
            NaN-aware minimum value.
        """
        return np.nanmin(self.values)

    @property
    def max(self) -> float:
        """Return maximum finite property value.

        Returns
        -------
        float
            NaN-aware maximum value.
        """
        return np.nanmax(self.values)

    @property
    def mean(self) -> float:
        """Return arithmetic mean of finite values.

        Returns
        -------
        float
            NaN-aware mean value.
        """
        return np.nanmean(self.values)

    @property
    def median(self) -> float:
        """Return median of finite values.

        Returns
        -------
        float
            NaN-aware median value.
        """
        return np.nanmedian(self.values)

    @property
    def std(self) -> float:
        """Return standard deviation of finite values.

        Returns
        -------
        float
            NaN-aware standard deviation.
        """
        return np.nanstd(self.values)


    # ----------------------------
    # Assignment API
    # ----------------------------
    def fill_normal(
        self,
        mean: float,
        std: float,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
        min: float | None = None,
        max: float | None = None,
        seed: int | None = None,
    ) -> "GridProperty":
        """Fill target cells with samples from a normal distribution.

        Parameters
        ----------
        mean : float
            Mean of the normal distribution.
        std : float
            Standard deviation of the normal distribution.
        zone : str or Zone or None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, only active cells are assigned.
        min : float, optional, default None
            Minimum value after adding noise (clipping).
        max : float, optional, default None
            Maximum value after adding noise (clipping).
        seed : int or None, optional, default None
            Seed for reproducible sampling.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        ValueError
            If ``std`` is negative.
        """
        if std < 0:
            raise ValueError(f"`std` must be >= 0, got {std}.")

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        n = int(np.count_nonzero(mask))

        rng = np.random.default_rng(seed)
        values = rng.normal(mean, std, size=n)

        if min is not None:
            values = np.maximum(values, min)
        if max is not None:
            values = np.minimum(values, max)

        self.values[mask] = values
        return self

    def apply(
        self,
        func: Callable[..., Any],
        *,
        source: str | GridProperty | Sequence[str | GridProperty],
        zone: str | Zone | None = None,
        include_inactive: bool = True,
    ) -> GridProperty:
        """
        Apply a function to geometric sources and/or existing properties,
        then assign the result into this property.

        Parameters
        ----------
        func : callable
            Function applied to the resolved source arrays.
        source : str | GridProperty | sequence of these
            Input source(s) for the function.

            Supported built-in string sources:
            - "x"           : cell-center x coordinate
            - "y"           : cell-center y coordinate
            - "depth", "z"  : cell-center depth (positive downward)
            - "top"         : top z of cell
            - "bottom"      : bottom z of cell
            - "thickness"   : cell thickness
            - "active"      : 1 for active cells, 0 for inactive

            You may also pass another GridProperty, or a tuple/list mixing them.

        zone : str | Zone | None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, only active cells are assigned.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Examples
        --------
        poro.apply(lambda z: 0.32 - 0.00015 * z, source="depth")

        perm.apply(lambda p: 1000 * p**3, source=poro)

        perm.apply(
            lambda z, p: (1000 * p**3) * np.exp(-z / 3000.0),
            source=("depth", poro),
        )

        Raises
        ------
        TypeError
            If ``func`` is not callable or ``source`` type is invalid.
        ValueError
            If resolved source dimensions are incompatible or function output
            shape is unsupported.
        """
        if not callable(func):
            raise TypeError("`func` must be callable (e.g. a function or lambda).")

        if isinstance(source, (str, GridProperty)):
            sources = (source,)
        elif isinstance(source, Sequence):
            if len(source) == 0:
                raise ValueError("`source` cannot be empty.")
            sources = tuple(source)
        else:
            raise TypeError(
                "`source` must be str, GridProperty, or a sequence of them."
            )

        resolved = [self.grid._resolve_source(src) for src in sources]
        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)

        # Validate resolved source shapes
        for arr in resolved:
            if arr.shape[:3] != self.grid.shape:
                raise ValueError(
                    f"Resolved source has invalid leading shape {arr.shape[:3]}; "
                    f"expected {self.grid.shape}."
                )

        # Slice only target cells for efficient evaluation
        inputs = []
        for arr in resolved:
            if arr.ndim == 3:
                inputs.append(arr[mask])          # (n,)
            elif arr.ndim == 4:
                inputs.append(arr[mask, :])       # (n, m)
            else:
                raise ValueError(
                    f"Resolved source must have ndim 3 or 4, got {arr.ndim}."
                )

        result = func(*inputs)
        result = np.asarray(result)

        n_target = int(np.count_nonzero(mask))

        # Allow scalar return
        if result.shape == ():
            result = np.full(n_target, result, dtype=float)

        # Allow vector return for scalar-like sources
        elif result.shape == (n_target,):
            result = result.astype(float, copy=False)

        else:
            raise ValueError(
                f"`func` must return either a scalar or shape ({n_target},), "
                f"got {result.shape}."
            )

        self.values[mask] = result
        return self

    def fill(
        self,
        value: float | int,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
    ) -> GridProperty:
        """Fill target cells with a constant numeric value.

        Parameters
        ----------
        value : float or int
            Value to assign.
        zone : str | Zone | None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, only active cells are assigned.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        TypeError
            If ``value`` is not numeric.
        """
        if not isinstance(value, (int, float)):
            raise TypeError("`value` must be a float or int.")

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        self.values[mask] = value
        return self
    
            
    def fill_lognormal(
        self,
        mean: float,
        std: float,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
        min: float | None = None,
        max: float | None = None,
        seed: int | None = None,
    ) -> "GridProperty":
        """Fill target cells with samples from a lognormal distribution.

        Parameters
        ----------
        mean : float
            Mean in linear space (e.g. permeability mean).
        std : float
            Standard deviation in linear space.
        zone : str | Zone | None, optional, default None
            Restrict to zone.
        include_inactive : bool, default True
            When False, only active cells are assigned.
        min : float | None, default None
            Optional lower bound.
        max : float | None, default None
            Optional upper bound.
        seed : int | None, default None
            Random seed.

        Notes
        -----
        Internally converts linear mean/std to log-space parameters.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        ValueError
            If ``mean <= 0`` or ``std < 0``.
        """
        if mean <= 0:
            raise ValueError("`mean` must be > 0 for lognormal distribution.")
        if std < 0:
            raise ValueError("`std` must be >= 0.")

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        n = int(np.count_nonzero(mask))

        if n == 0:
            return self

        # Convert linear → log space
        variance = std**2
        sigma_log = np.sqrt(np.log(1 + variance / mean**2))
        mu_log = np.log(mean) - 0.5 * sigma_log**2

        rng = np.random.default_rng(seed)
        values = rng.lognormal(mean=mu_log, sigma=sigma_log, size=n)

        # Optional clipping
        if min is not None:
            values = np.maximum(values, min)
        if max is not None:
            values = np.minimum(values, max)

        self.values[mask] = values
        return self

    def fill_uniform(
        self,
        low: float,
        high: float,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
        seed: int | None = None,
    ) -> "GridProperty":
        """Fill target cells with samples from a uniform distribution.

        Parameters
        ----------
        low : float
            Lower bound of the distribution.
        high : float
            Upper bound of the distribution (must be ``>= low``).
        zone : str or Zone or None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, inactive cells are excluded.
        seed : int or None, optional, default None
            Seed for reproducible sampling.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        ValueError
            If ``high < low``.
        """
        if high < low:
            raise ValueError(f"`high` must be >= `low`, got {high} < {low}.")

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        n = int(np.count_nonzero(mask))

        rng = np.random.default_rng(seed)
        self.values[mask] = rng.uniform(low, high, size=n)
        return self

    def fill_nan(
        self,
        value: float | int,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
    ) -> GridProperty:
        """Fill ``NaN`` entries with a constant value.

        Parameters
        ----------
        value : float or int
            Replacement value for ``NaN`` cells.
        zone : str or Zone or None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, inactive cells are excluded.

        Returns
        -------
        GridProperty
            Self, for chaining.
        """
        mask = np.isnan(self.values) & self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        self.values[mask] = value
        return self

    def from_array(
        self,
        values: ArrayLike,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = True,
    ) -> GridProperty:
        """Assign values from an array, optionally scoped by zone/active mask.

        Parameters
        ----------
        values : ndarray
            Source array shaped ``(nk, nj, ni)``.
        zone : str or Zone or None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, inactive cells are excluded.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        ValueError
            If ``values`` shape does not match grid shape.
        """
        values = np.asarray(values)

        if values.shape != self.grid.shape:
            raise ValueError(
                f"`values` shape {values.shape} != grid shape {self.grid.shape}."
            )
        
        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        self.values[mask] = values[mask]
        return self


    # ----------------------------
    # Well-based assignment
    # ---------------------------- 
    
    def from_wells(
        self,
        wells: Sequence["VerticalWell"],
        interpolator: BaseInterpolator,
        *,
        source: str | None = None,
        mode: Literal["xy", "xyz"] = "xy",
        zone: str | Zone | None = None,
        location: Literal["center", "top", "bottom"] = "center",
        include_inactive: bool = True,
    ) -> "GridProperty":
        """Populate this property by interpolating well samples.

        Parameters
        ----------
        wells : sequence of VerticalWell
            Wells containing property samples.
        interpolator : BaseInterpolator
            Interpolator instance with `fit(points, values)` and `predict(query)` methods.
        source : str | None, optional, default None
            Sample property name to read from wells. Defaults to `self.name`.
        location : {"center", "top", "bottom"}, default "center"
            Grid cell location used as interpolation target.
        zone : str | Zone | None, optional, default None
            Restrict assignment to a zone.
        include_inactive : bool, default True
            When False, only active cells are assigned.
        mode : {"xy", "xyz"}, default "xy"
            If "xyz", every sample must have depth values.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Raises
        ------
        ValueError
            If mode, source data, or interpolator output shape is invalid.
        TypeError
            If ``interpolator`` is not a ``BaseInterpolator`` or wells contain
            invalid entries.
        """
        source = self.name if source is None else source
        _validate_nonempty_string(source, "source")

        
        if mode not in ("xy", "xyz"):
            raise ValueError(f"Unsupported mode {mode!r}. Supported: 'xy', 'xyz'.")

        if not isinstance(interpolator, BaseInterpolator):
            raise TypeError("`interpolator` must be an instance of BaseInterpolator.")
         
        if not wells:
            raise ValueError("`wells` cannot be empty.")
        
        if not all(isinstance(well, VerticalWell) for well in wells):
            raise TypeError("All items in `wells` must be instances of VerticalWell.")
        
            

        coords, values = self._collect_well_samples(
            wells=wells,
            source=source,
            mode=mode,
        )

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        n_target = int(np.count_nonzero(mask))
        if n_target == 0:
            warnings.warn(
                "No target cells found for interpolation; no changes made to property values.",
                UserWarning,
            )
            return self

        targets = self._interpolation_targets(location=location)

        if mode == "xy":
            query = targets[..., :2][mask]
        elif mode == "xyz":
            query = targets[mask]
        else:
            raise RuntimeError(f"Unexpected interpolation mode: {mode!r}")

        interpolator.fit(coords, values)
        predicted = np.asarray(interpolator.predict(query), dtype=float)

        if predicted.shape != (n_target,):
            raise ValueError(
                f"Interpolator returned shape {predicted.shape}; "
                f"expected ({n_target},)."
            )

        self.values[mask] = predicted
        return self

    def to_grdecl(
        self, 
        path: str,
    ) -> None:
        """Write property values to a GRDECL file.

        Parameters
        ----------
        path : str
            Destination file path.

        Raises
        ------
        MissingEclipseKeywordError
            If this property has no Eclipse keyword.
        MissingPropertyValueError
            If value export fails due to missing values.
        """
        writer = GRDECLWriter()
        if self.eclipse_keyword is None:
            raise MissingEclipseKeywordError(property_name=self.name)
        
        try:
            writer.write_property( 
                path,
                values = self.values,
                keyword = self.eclipse_keyword
            )
        except GRDECLMissingValueError as e:
            raise MissingPropertyValueError(property_name=self.name) from e

    def summary(self) -> str:
        """Return a formatted textual summary for the property.

        Returns
        -------
        str
            Multi-line summary string containing metadata and statistics.
        """
        lines = [
            "Property Summary",
            "════════════════════════════════════════════════════════════════",
            f"Name              : {self.name}",
            f"Description       : {self.description}",
            f"Eclipse Keyword   : {self.eclipse_keyword}",
            f"Grid Shape        : {self.shape}",
            f"Min               : {self.min}",
            f"Max               : {self.max}",
            f"Mean              : {self.mean}",
            f"Median            : {self.median}",
            f"Std Dev           : {self.std}",
        ]
        return "\n".join(lines)
    


    def _collect_well_samples(
        self,
        wells: Sequence["VerticalWell"],
        source: str,
        mode: Literal["xy", "xyz"],
    ) -> tuple[np.ndarray, np.ndarray]:
        """Collect interpolation coordinates and values from well samples.

        Parameters
        ----------
        wells : sequence[VerticalWell]
            Wells providing sampled values.
        source : str
            Property key used to read values from each well.
        mode : {"xy", "xyz"}
            Coordinate mode for interpolation samples.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Coordinates with shape ``(n, 2)`` or ``(n, 3)`` and values with
            shape ``(n,)``.
        """
        coords_list: list[list[float]] = []
        values_list: list[float] = []

        require_z = mode == "xyz"

        for well in wells:
            depth_map = well.samples.get(source)
            existing_mode = well._sample_modes.get(source)

            if not depth_map:
                continue

            if require_z and existing_mode != "depth":
                raise ValueError(
                    f"Well '{well.name}' has sample '{source}' without depth values, "
                    "try `mode='xyz'`."
                )
            
            for z, value in depth_map.items():
                if mode == "xy":
                    coords_list.append([well.x, well.y])
                else:
                    coords_list.append([well.x, well.y, z])

                values_list.append(value)

        if not coords_list:
            raise ValueError(f"No samples found for source '{source}' in given wells.")

        coords = np.asarray(coords_list, dtype=float)
        values = np.asarray(values_list, dtype=float)

        has_duplicates = np.unique(coords, axis=0).shape[0] != coords.shape[0]
        if has_duplicates:
            raise ValueError("Duplicate sample locations detected. Please ensure each sample has a unique (x, y) for mode 'xy' or (x, y, z) coordinate for mode 'xyz'.")
      
        return coords, values

    def _interpolation_targets(
        self,
        location: Literal["center", "top", "bottom"] = "center",
    ) -> np.ndarray:
        """Build interpolation target coordinates for a cell location.

        Parameters
        ----------
        location : {"center", "top", "bottom"}, default "center"
            Cell location to target for interpolation.

        Returns
        -------
        np.ndarray
            Target coordinates in XYZ order.
        """
        match location:
            case "center":
                return self.grid.cell_centers

            case "top" | "bottom":
                corners = self.grid._compute_cell_corners()   # (nk, nj, ni, 8, 3)
                xy = np.mean(corners[..., :, :2], axis=-2)   # (nk, nj, ni, 2)

                zcorn = corners[..., 2]                      # (nk, nj, ni, 8)
                z_top = np.min(zcorn[..., :4], axis=-1)
                z_bottom = np.max(zcorn[..., 4:], axis=-1)
                z = z_top if location == "top" else z_bottom

                return np.concatenate([xy, z[..., np.newaxis]], axis=-1)

            case _:
                raise ValueError(
                    f"Unsupported location {location!r}. "
                    "Supported values are: 'center', 'top', 'bottom'."
                )
            
    
# ============================================================
# GridProperties
# ============================================================

class GridProperties:
    """Collection-style API for grid properties.

    Parameters
    ----------
    grid : CornerPointGrid
        Grid that owns the managed properties.

    Examples
    --------
    poro = grid.properties.create("poro", eclipse_keyword="PORO")
    poro.fill(0.25, zone="Upper")
    poro.fill(0.18, zone="Middle")

    permx = grid.properties.create("permx", eclipse_keyword="PERMX")
    permx.from_array(permx_values)

    poro2 = grid.properties["poro"]
    print(poro2.mean)

    """
    def __repr__(self):
        prop_names = ", ".join(self._grid._properties.keys())
        return f"GridProperties({prop_names})"

    def __init__(self, grid: "CornerPointGrid") -> None:
        """Initialize a property manager bound to one grid."""
        self._grid = grid

    def create(
        self,
        name: str,
        *,
        eclipse_keyword: str | None = None,
        description: str | None = None,
        fill_value: float = np.nan,
    ) -> GridProperty:
        """Create and register a new property on the grid.

        Parameters
        ----------
        name : str
            Property name (must be unique and non-reserved).
        eclipse_keyword : str or None, optional
            Keyword for GRDECL export.
        description : str or None, optional
            Human-readable description.
        fill_value : float, default NaN
            Initial fill value for all cells.

        Returns
        -------
        GridProperty
            Newly created property attached to the grid.

        Raises
        ------
        ExistingPropertyNameError
            If a property with the same name already exists.
        ReservedPropertyNameError
            If ``name`` conflicts with built-in grid attributes.
        """
        name = self._validate_property_name(name)

        if name in self._grid._properties:
            raise ExistingPropertyNameError(property_name=name)

        values = np.full(self._grid.shape, fill_value, dtype=float)

        prop = GridProperty(
            grid=self._grid,
            name=name,
            values=values,
            eclipse_keyword=eclipse_keyword,
            description=description,
        )
        self._grid._properties[name] = prop
        return prop

    def __getitem__(self, name: str) -> GridProperty:
        """Return a property by name.

        Parameters
        ----------
        name : str
            Property name.

        Returns
        -------
        GridProperty
            Matching property instance.

        Raises
        ------
        KeyError
            If no property with the given name exists.
        """
        try:
            return self._grid._properties[name]
        except KeyError as e:
            raise KeyError(f"Property '{name}' does not exist.") from e

    def __contains__(self, name: str) -> bool:
        """Check whether a property name exists.

        Parameters
        ----------
        name : str
            Property name to query.

        Returns
        -------
        bool
            ``True`` if the property exists, else ``False``.
        """
        return name in self._grid._properties

    @property
    def names(self) -> list[str]:
        """Return property names in insertion order.

        Returns
        -------
        list of str
            Registered property names.
        """
        return list(self._grid._properties.keys())

    @property
    def items(self) -> ItemsView[str, GridProperty]:
        """Return name/property view.

        Returns
        -------
        ItemsView[str, GridProperty]
            Dictionary-style items view over managed properties.
        """
        return self._grid._properties.items()

    @property
    def values(self) -> ValuesView[GridProperty]:
        """Return values view of property instances.

        Returns
        -------
        ValuesView[GridProperty]
            Dictionary-style values view over managed properties.
        """
        return self._grid._properties.values()

    @staticmethod
    def _validate_property_name(name: str) -> str:
        """Validate a candidate property name.

        Parameters
        ----------
        name : str
            Candidate name to validate.

        Returns
        -------
        str
            Validated name.
        """
        from .cornerpoint import RESERVED_GRID_PROPERTY_NAMES
        
        if not isinstance(name, str):
            raise TypeError(f"`name` must be str, got {type(name).__name__}.")

        if not name.strip():
            raise ValueError("`name` cannot be empty.")

        if name in RESERVED_GRID_PROPERTY_NAMES:
            raise ReservedPropertyNameError(property_name=name, reserved_names=RESERVED_GRID_PROPERTY_NAMES)

        return name
