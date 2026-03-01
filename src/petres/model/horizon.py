from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from ..interpolators.base import BaseInterpolator
from .zone import Zone


@dataclass
class Horizon:
    """
    Continuous horizon z = f(x, y), defined by scattered picks + an interpolator.

    Required at init:
      - xy picks (n,2)
      - z picks  (n,)
      - interpolator (BaseInterpolator) which will be fitted in __init__
    """
    name: str
    interpolator: BaseInterpolator
    xy: np.ndarray = field(repr=False)
    z: np.ndarray = field(repr=False)
    store_picks: bool = True  

    def __post_init__(self):
        if self.interpolator.is_allowed_dim(2) is False:
            raise TypeError(
                f"Horizon '{self.name}' requires an interpolator that supports 2D coordinates (x,y). "
                f"But {self.interpolator.allowed_dims} were allowed.")

        self.xy = np.asarray(self.xy, dtype=float)
        self.z = np.asarray(self.z, dtype=float)

        if self.xy.ndim != 2 or self.xy.shape[1] != 2:
            raise ValueError(f"Horizon '{self.name}': xy must be shape (n,2). Got {self.xy.shape}")
        if self.z.ndim != 1 or self.z.shape[0] != self.xy.shape[0]:
            raise ValueError(f"Horizon '{self.name}': z must be shape (n,) matching xy. Got {self.z.shape}")

        # Fit interpolator; BaseInterpolator validates + sets dim_
        self.interpolator.fit(self.xy, self.z)

        if not self.store_picks:
            # free memory if user doesn't need provenance
            self.xy = np.empty((0, 2), dtype=float)
            self.z = np.empty((0,), dtype=float)

    def to_zone(self, name: str, depth: float) -> Zone:

        """
        Create a Zone by shifting this horizon by depth.

        Parameters
        ----------
        name : str
            Zone name.
        depth : float
            Vertical shift applied to create the second horizon.
            Positive depth means deeper if z increases downward.
        """
        if depth == 0:
            raise ValueError("'depth' cannot be zero.")

        if self.xy.size == 0:
            raise ValueError(
                "Cannot generate second horizon because picks were not stored "
                "(store_picks=False)."
            )

        new_z = self.z + depth

        new_interp = type(self.interpolator)()

        other = Horizon(
            name=f"{self.name}_shifted",
            interpolator=new_interp,
            xy=self.xy.copy(),
            z=new_z,
            store_picks=self.store_picks,
        )

        # Determine top/base based on relative depth
        if depth > 0:
            # shifted horizon is deeper
            return Zone(name=name, top=self, base=other)
        else:
            return Zone(name=name, top=other, base=self)

    def sample(self, xy: np.ndarray) -> np.ndarray:
        xy = np.asarray(xy, dtype=float)
        if xy.ndim != 2 or xy.shape[1] != 2:
            raise ValueError(f"Horizon '{self.name}': sample expects xy shape (n,2). Got {xy.shape}")
        return self.interpolator.predict(xy)

    def to_grid(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        x = np.asarray(x, dtype=float).ravel()
        y = np.asarray(y, dtype=float).ravel()
        xx, yy = np.meshgrid(x, y)
        pts = np.column_stack([xx.ravel(), yy.ravel()])
        return self.sample(pts).reshape(y.size, x.size)
    

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
    ):
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_horizon(self, x=x, y=y, xlim=xlim, ylim=ylim, nx=nx, ny=ny, dx=dx, dy=dy, color=color)
        viewer.show()