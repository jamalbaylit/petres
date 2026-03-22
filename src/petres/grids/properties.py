from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Union
import numpy as np

from ..models.zone import Zone

@dataclass
class GridProperty:
    """
    Cell-based property defined on a grid with shape (nk, nj, ni).
    """
    grid: "CornerPointGrid"= field(repr=False)
    values: Optional[np.ndarray] = None 
    name: Optional[str] = None
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

    def add_constant(
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

    def add_array(
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


    
# ============================================================
# GridProperties
# ============================================================

class GridProperties:
    """
    Collection-style API for grid properties.

    Examples
    --------
    poro = grid.properties.create("poro", eclipse_keyword="PORO")
    poro.add_constant(0.25, zone="Upper")
    poro.add_constant(0.18, zone="Middle")

    permx = grid.properties.create("permx", eclipse_keyword="PERMX")
    permx.add_array(permx_values)

    poro2 = grid.properties["poro"]
    print(poro2.mean)
    """

    def __init__(self, grid: "CornerPointGrid") -> None:
        self._grid = grid

    def create(
        self,
        name: str,
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

    def names(self) -> list[str]:
        return list(self._grid._properties.keys())

    def items(self):
        return self._grid._properties.items()

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


