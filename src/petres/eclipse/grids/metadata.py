from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
import numpy as np


MAP_UNITS = frozenset({
    "METRES",
    "FEET",
    "LAB",
    "PVT-M",
})



@dataclass(slots=True)
class EclipseGridMetadata:
    """
    Eclipse-specific metadata preserved for round-trip GRDECL export.

    Notes
    -----
    These fields are not required for internal grid calculations, but are
    preserved so imported GRDECL files can be re-exported without losing
    optional Eclipse keywords.
    """

    mapaxes: Any | None = None
    mapunits: Any | None = None
    gridunit: Any | None = None
    coordsys: Any | None = None
    pinch: Any | None = None

    def __post_init__(self) -> None:
        if self.mapaxes is not None:
            self.mapaxes = self._validate_mapaxes(self.mapaxes)
            
        if self.mapunits is not None:
            self.mapunits = self._validate_mapunits(self.mapunits)

        if self.gridunit is not None:
            self.gridunit = self._validate_gridunit(self.gridunit)

        if self.coordsys is not None:
            self.coordsys = self._validate_coordsys(self.coordsys)

        if self.pinch is not None:
            self.pinch = self._validate_pinch(self.pinch)

    def _validate_pinch(self, pinch: Any) -> Any:
        return pinch
    
    def _validate_coordsys(self, coordsys: Any) -> Any:
        # return str(coordsys)
        return coordsys
    
    def _validate_mapaxes(self, mapaxes: Any) -> Any:
        # mapaxes = np.asarray(mapaxes, dtype=float)

        # if  mapaxes.shape != (6,):
        #     raise ValueError(
        #         "`mapaxes` must contain exactly 6 values."
        #     )

        # if not np.all(np.isfinite(mapaxes)):
        #     raise ValueError(
        #         "`mapaxes` must contain only finite numbers."
        #     )

        # x1, y1, x2, y2, x3, y3 = mapaxes

        # # Prevent degenerate axes
        # v1 = np.array([x1 - x2, y1 - y2])
        # v2 = np.array([x3 - x2, y3 - y2])

        # if np.linalg.norm(v1) == 0:
        #     raise ValueError(
        #         "MAPAXES Y-axis point cannot equal origin."
        #     )

        # if np.linalg.norm(v2) == 0:
        #     raise ValueError(
        #         "MAPAXES X-axis point cannot equal origin."
        #     )
        return mapaxes

    def _validate_mapunits(self, mapunits: Any) -> Any:
        # mapunits = str(mapunits).upper()
        # if mapunits not in MAP_UNITS:
        #     raise ValueError(
        #         f"Unsupported MAPUNITS '{mapunits}'. "
        #         f"Supported values: {sorted(MAP_UNITS)}"
        #     )
        return mapunits

    def _validate_gridunit(self, gridunit: Any) -> Any:
        # gridunit = str(gridunit).upper()
        return gridunit
    
