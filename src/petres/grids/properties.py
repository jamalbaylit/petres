from __future__ import annotations

from typing import Any, Callable, Callable, Literal, Optional, Sequence, Tuple, Dict, Union
from dataclasses import dataclass, field
import numpy as np
import warnings

from .._validation import _validate_nonempty_string
from ..interpolators.base import BaseInterpolator
from ..models.wells import VerticalWell
from ..models.zone import Zone

@dataclass
class GridProperty:
    """
    Cell-based property defined on a grid with shape (nk, nj, ni).
    """
    name: str = field(repr=True)
    grid: "CornerPointGrid"= field(repr=False)
    values: Optional[np.ndarray] = None 
    eclipse_keyword: Optional[str] = None                 # Eclipse keyword (PORO, PERMX, ...)
    description: Optional[str] = None

    def __post_init__(self):
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
            keyword = self.eclipse_keyword.strip().upper()
            if not keyword:
                raise ValueError("`eclipse_keyword` cannot be empty.")
            self.eclipse_keyword = keyword

        if self.name is not None:
            if not isinstance(self.name, str):
                raise TypeError("`name` must be a string or None.")
            if not self.name.strip():
                raise ValueError("`name` cannot be empty.")

    def show(self, show_inactive: bool = False, cmap: Optional[str] = 'turbo', **kwargs) -> None:
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_grid(grid=self.grid, show_inactive=show_inactive, scalars=self.values, cmap=cmap, **kwargs)
        viewer.show()
                          
    @property
    def shape(self) -> Tuple[int, int, int]:
        return self.values.shape

    @property
    def nk(self) -> int: return self.shape[0]

    @property
    def nj(self) -> int: return self.shape[1]
    
    @property
    def ni(self) -> int: return self.shape[2]
    
    @property
    def n_cells(self) -> int: return self.nk * self.nj * self.ni

    @property
    def min(self) -> float: return np.nanmin(self.values)

    @property
    def max(self) -> float: return np.nanmax(self.values)

    @property
    def mean(self) -> float: return np.nanmean(self.values)

    @property
    def median(self) -> float: return np.nanmedian(self.values)

    @property
    def std(self) -> float: return np.nanstd(self.values)


    # ----------------------------
    # Assignment API
    # ----------------------------
    def fill_normal(
        self,
        mean: float,
        std: float,
        *,
        zone: str | Zone | None = None,
        include_inactive: bool = False,
        min: float | None = None,
        max: float | None = None,
        seed: int | None = None,
    ):
        """
        Add normally distributed random noise to this property.

        Parameters
        ----------
        mean : float
            Mean of the normal distribution.
        std : float
            Standard deviation of the normal distribution.
        min : float, optional
            Minimum value after adding noise (clipping).
        max : float, optional
            Maximum value after adding noise (clipping).

        Returns
        -------
        GridProperty
            Self, for chaining.
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
        source: str | "GridProperty" | Sequence[str | "GridProperty"] = "z_center",
        zone: Optional[str | Zone] = None,
        include_inactive: bool = False,
    ) -> "GridProperty":
        """
        Apply a function to geometric sources and/or existing properties,
        then assign the result into this property.

        Parameters
        ----------
        func : callable
            Function applied to the resolved source arrays.
        source : str | GridProperty | sequence of these, default "z_center"
            Input source(s) for the function.

            Supported built-in string sources:
            - "x"         : cell-center x coordinate
            - "y"         : cell-center y coordinate
            - "z"         : cell-center z coordinate
            - "top"       : top z of cell
            - "bottom"    : bottom z of cell
            - "thickness" : cell thickness

            You may also pass another GridProperty, or a tuple/list mixing them.

        zone : str | Zone | None, optional
            Restrict assignment to a zone.
        include_inactive : bool, default False
            If False, only active cells are assigned.

        Returns
        -------
        GridProperty
            Self, for chaining.

        Examples
        --------
        poro.apply(lambda z: 0.32 - 0.00015 * z, source="z_center")

        perm.apply(lambda p: 1000 * p**3, source=poro)

        perm.apply(
            lambda z, p: (1000 * p**3) * np.exp(-z / 3000.0),
            source=("z_center", poro),
        )
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
        zone: Optional[str | Zone] = None,
        include_inactive: bool = False,
    ) -> GridProperty:
        """
        Fill this property with a constant value.

        Parameters
        ----------
        value : float or int
            Value to assign.
        zone : str | Zone | None, optional
            Restrict assignment to a zone.
        include_inactive : bool, default False
            If False, only active cells are assigned.

        Returns
        -------
        GridProperty
            Self, for chaining.
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
        include_inactive: bool = False,
        min: float | None = None,
        max: float | None = None,
        seed: int | None = None,
    ) -> "GridProperty":
        """
        Fill property by sampling from a lognormal distribution.

        Parameters
        ----------
        mean : float
            Mean in linear space (e.g. permeability mean).
        std : float
            Standard deviation in linear space.
        zone : str | Zone | None, optional
            Restrict to zone.
        include_inactive : bool, default False
            If False, only active cells are assigned.
        min : float | None
            Optional lower bound.
        max : float | None
            Optional upper bound.
        seed : int | None
            Random seed.

        Notes
        -----
        Internally converts linear mean/std to log-space parameters.
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
        include_inactive: bool = False,
        seed: int | None = None,
    ) -> "GridProperty":
        if high < low:
            raise ValueError(f"`high` must be >= `low`, got {high} < {low}.")

        mask = self.grid._target_mask(zone=zone, include_inactive=include_inactive)
        n = int(np.count_nonzero(mask))

        rng = np.random.default_rng(seed)
        self.values[mask] = rng.uniform(low, high, size=n)
        return self

    def fill(
        self,
        value: float | int,
        *,
        zone: str | Zone | None = None,
    ) -> GridProperty:
        if zone is not None:
            mask = self.grid._zone_mask(zone)
            self.values[mask] = value
        else:
            self.values.fill(value)
        return self

    def from_array(
        self,
        values: np.ndarray,
        zone: str | Zone | None = None,
    ) -> GridProperty:
        values = np.asarray(values)

        if values.shape != self.grid.shape:
            raise ValueError(
                f"`values` shape {values.shape} != grid shape {self.grid.shape}."
            )

        if zone is not None:
            mask = self.grid._zone_mask(zone)
            self.values[mask] = values[mask]
        else:
            self.values = values
        return self


    # ----------------------------
    # Well-based assignment
    # ---------------------------- 
    
    def from_wells(
        self,
        wells: Sequence["VerticalWell"],
        interpolator,
        *,
        source: str | None = None,
        mode: Literal["xy", "xyz"] = "xy",
        zone: str | Zone | None = None,
        location: Literal["center", "top", "bottom"] = "center",
        include_inactive: bool = False,
    ) -> "GridProperty":
        """
        Populate this property by interpolating well samples.

        Parameters
        ----------
        wells : sequence of VerticalWell
            Wells containing property samples.
        interpolator :
            Interpolator instance with `fit(points, values)` and `predict(query)` methods.
        source : str | None, optional
            Sample property name to read from wells. Defaults to `self.name`.
        location : {"center", "top", "bottom"}, default "center"
            Grid cell location used as interpolation target.
        zone : str | Zone | None, optional
            Restrict assignment to a zone.
        include_inactive : bool, default False
            If False, only active cells are assigned.
        mode : {"xy", "xyz"}, default "xy"
            If "xyz", every sample must have depth values.

        Returns
        -------
        GridProperty
            Self, for chaining.
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
        *,
        include_actnum: bool = True,
    ) -> None:
        return self.grid.to_grdecl(
            path=path, 
            properties=[self.name], 
            include_actnum=include_actnum
        )

    def _collect_well_samples(
        self,
        wells: Sequence["VerticalWell"],
        source: str,
        mode: Literal["xy", "xyz"],
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Collect well samples into interpolation coordinate/value arrays.

        Returns
        -------
        coords : ndarray
            Shape (n, 2) for XY mode or (n, 3) for XYZ mode.
        values : ndarray
            Shape (n,).
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
        """
        Return interpolation target coordinates of shape (nk, nj, ni, 3).
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
    """
    Collection-style API for grid properties.

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

    def __init__(self, grid: "CornerPointGrid") -> None:
        self._grid = grid

    def create(
        self,
        name: str,
        *,
        eclipse_keyword: Optional[str] = None,
        description: Optional[str] = None,
        fill_value: float = np.nan,
    ) -> GridProperty:
        name = self._normalize_name(name)

        if name in self._grid._properties:
            raise ValueError(f"Property '{name}' already exists.")

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
        try:
            return self._grid._properties[name]
        except KeyError as e:
            raise KeyError(f"Property '{name}' does not exist.") from e

    def __contains__(self, name: str) -> bool:
        return name in self._grid._properties

    @property
    def names(self) -> list[str]:
        return list(self._grid._properties.keys())

    @property
    def items(self):
        return self._grid._properties.items()

    @property
    def values(self):
        return self._grid._properties.values()

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str):
            raise TypeError(f"`name` must be str, got {type(name)}.")
        name = name.strip()
        if not name:
            raise ValueError("`name` cannot be empty.")
        return name


