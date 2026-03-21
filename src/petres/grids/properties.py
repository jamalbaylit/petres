from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Union
import numpy as np

from petres.models.zone import Zone


@dataclass
class GridProperty:
    """
    Cell-based property defined on a grid with shape (nk, nj, ni).
    """
    values: np.ndarray
    name: Optional[str] = None
    eclipse_keyword: Optional[str] = None                 # Eclipse keyword (PORO, PERMX, ...)
    description: Optional[str] = None

    def __post_init__(self):
        assert isinstance(self.values, np.ndarray), f"values must be a numpy array, got {type(self.values)}"
        assert self.values.ndim == 3, f"Values must be 3D, got shape {self.values.shape}"
        # make sure keyword has zero space or tab etc.
        if self.eclipse_keyword is not None:
            assert self.eclipse_keyword.strip() == self.eclipse_keyword, f"`eclipse_keyword` must not have leading/trailing whitespace, got '{self.eclipse_keyword}'"
            self.eclipse_keyword = self.eclipse_keyword.upper()

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


# --------------------------------------------------
# GridProperties (manager / API)
# --------------------------------------------------

class GridProperties:
    def __init__(self, grid: "CornerPointGrid") -> None:
        self._grid = grid

    # ---------- Public API ----------

    def add_constant(
        self,
        name: str,
        value: float | int,
        zone: Union[str, "Zone", None] = None,
        *,
        eclipse_keyword: Optional[str] = None,
        description: Optional[str] = None,
    ) -> GridProperty:
        zone_name = self._normalize_zone(zone)
        mask = self._zone_mask(zone_name)

        prop = self._ensure_property(name, eclipse_keyword, description)

        prop.values[mask] = value
        return prop

    def add_array(
        self,
        name: str,
        values: np.ndarray,
        zone: Union[str, "Zone", None] = None,
        *,
        eclipse_keyword: Optional[str] = None,
        description: Optional[str] = None,
    ) -> GridProperty:
        values = np.asarray(values)

        if values.shape != self._grid.shape:
            raise ValueError(
                f"`values` shape {values.shape} != grid shape {self._grid.shape}"
            )

        zone_name = self._normalize_zone(zone)
        mask = self._zone_mask(zone_name)

        prop = self._ensure_property(name, eclipse_keyword, description)

        prop.values[mask] = values[mask]
        return prop

    def __getitem__(self, name: str) -> GridProperty:
        try:
            return self._grid._properties[name]
        except KeyError:
            raise KeyError(f"Property '{name}' does not exist.")

    def names(self) -> list[str]:
        return list(self._grid._properties.keys())

    # ---------- Internal helpers ----------

    def _ensure_property(
        self,
        name: str,
        eclipse_keyword: Optional[str],
        description: Optional[str],
    ) -> GridProperty:
        if name not in self._grid._properties:
            values = np.full(self._grid.shape, np.nan, dtype=float)
            self._grid._properties[name] = GridProperty(
                values=values,
                name=name,
                eclipse_keyword=eclipse_keyword,
                description=description,
            )
        return self._grid._properties[name]

    def _normalize_zone(self, zone) -> Optional[str]:
        if zone is None:
            return None

        # Lazy import style (avoid circular dependency)
        if hasattr(zone, "name"):
            zone = zone.name

        if not isinstance(zone, str):
            raise TypeError("`zone` must be str, Zone, or None")

        zone = zone.strip()
        if not zone:
            raise ValueError("`zone` cannot be empty")

        return zone

    def _zone_mask(self, zone_name: Optional[str]) -> np.ndarray:
        grid = self._grid

        # Start from active cells
        mask = grid.active.copy()

        if zone_name is None:
            return mask

        if grid.zone_index is None:
            raise ValueError("Grid has no zones defined")

        zone_id = self._zone_name_to_id(zone_name)
        return mask & (grid.zone_index == zone_id)

    def _zone_name_to_id(self, zone_name: str) -> int:
        for zid, name in self._grid.zone_names.items():
            if name == zone_name:
                return zid
        raise ValueError(f"Zone '{zone_name}' not found")


