from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence
import numpy as np


@dataclass(frozen=True)
class Zone:
    name: str
    top: "Horizon"
    base: "Horizon"
    levels: tuple[float, ...] = (0.0, 1.0)  # default: single layer

    @property
    def n_layers(self) -> int:
        """Number of layers in this zone."""
        return len(self.levels) - 1
    
    def thickness(self, xy: np.ndarray) -> np.ndarray:
        return self.base.sample(xy) - self.top.sample(xy)
    
    def show(
        self,
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        nx: int | None = None,
        ny: int | None = None,
        dx: float | None = None,
        dy: float | None = None,

        color: Any | None = None,
        show_layers: bool = True,
        show_edges: bool = True,
    ):
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_zone(
            self, x=x, y=y, xlim=xlim, ylim=ylim, nx=nx, ny=ny, dx=dx, dy=dy, 
            color=color,
            show_layers=show_layers,
            show_edges=show_edges,
        )
        viewer.show()

    def divide(
        self,
        *,
        nk: int | None = None,
        fractions: Sequence[float] | None = None,
        levels: Sequence[float] | None = None,
    ) -> "Zone":
        """
        Define internal layering for this zone (single method, Petrel-like).

        Exactly one of {nk, fractions, levels} may be provided.
        If none are provided, the zone becomes single-layer (levels=(0,1)).

        Parameters
        ----------
        nk
            Number of layers divided equally. Must be >= 2.
        fractions
            Relative layer thicknesses (positive). Will be normalized to sum to 1.
            Example: [0.1, 0.2, 0.7] -> levels [0, 0.1, 0.3, 1.0].
        levels
            Normalized interface levels in [0, 1], strictly increasing,
            starting at 0 and ending at 1.
            Example: [0, 0.3, 1] -> 2 layers.
 
        Returns
        -------
        Zone
            New Zone instance with updated `levels`.
        """
        provided = [nk is not None, fractions is not None, levels is not None]
        n_provided = int(sum(provided))

        if n_provided != 1:
            raise ValueError(f"{self.__class__.__name__}.divide(): provide only one of nk, fractions or levels.")

        if levels is not None:
            lv = self._validate_levels(levels)
        elif fractions is not None:
            lv = self._fractions_to_levels(fractions)
        elif nk is not None:
            lv = self._nk_to_levels(nk)
        else:
            raise ValueError("Unreachable code: exactly one of nk, fractions, levels must be provided.")
        object.__setattr__(self, "levels", lv)
        return self

    def _validate_levels(self, levels: Sequence[float]) -> tuple[float, ...]:
        lv = np.asarray(list(levels), dtype=float)

        if lv.ndim != 1 or lv.size < 2:
            raise ValueError("'levels' must be a 1D sequence with at least 2 values.")
        if np.any(~np.isfinite(lv)):
            raise ValueError("'levels' must be finite.")
        if lv[0] != 0:
            raise ValueError("'levels[0]' must be 0.0.")
        if lv[-1] != 1:
            raise ValueError("'levels[-1]' must be 1.0.")
        if np.any(lv < 0) or np.any(lv > 1):
            raise ValueError("'levels' must lie within [0, 1].")
        if np.any(np.diff(lv) <= 0):
            raise ValueError("'levels' must be strictly increasing.")

        lv[0] = 0.0
        lv[-1] = 1.0
        return tuple(float(x) for x in lv)


    def _fractions_to_levels(self, fractions: Sequence[float]) -> tuple[float, ...]:
        fr = np.asarray(list(fractions), dtype=float)
        if fr.ndim != 1 or fr.size == 0:
            raise ValueError("`fractions` must be a non-empty 1D sequence.")
        if np.any(~np.isfinite(fr)) or np.any(fr <= 0):
            raise ValueError("`fractions` must be finite and > 0.")

        fr = fr / float(fr.sum())  # normalize
        lv = np.concatenate(([0.0], np.cumsum(fr)))
        lv[-1] = 1.0  # numeric cleanup
        return self._validate_levels(lv)

    def _nk_to_levels(self, nk: int) -> tuple[float, ...]:
        if not isinstance(nk, int):
            raise TypeError("'nk' must be an int.")
        if not nk >= 2:
            raise ValueError("'nk' must be >= 2.")
    
        lv = np.linspace(0.0, 1.0, nk + 1, dtype=float)
        return self._validate_levels(lv)


    # def to_grid(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    #     x = np.asarray(x, dtype=float).ravel()
    #     y = np.asarray(y, dtype=float).ravel()
    #     xx, yy = np.meshgrid(x, y)
    #     pts = np.column_stack([xx.ravel(), yy.ravel()])
    #     top_z = self.top.sample(pts).reshape(y.size, x.size)
    #     base_z = self.base.sample(pts).reshape(y.size, x.size)
    #     return xx, yy, top_z, base_z