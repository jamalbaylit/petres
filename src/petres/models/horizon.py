from __future__ import annotations

from typing import Any, Iterable, Optional, Literal
from dataclasses import dataclass, field
import numpy as np


from ..interpolators.base import BaseInterpolator
from ..models.wells import VerticalWell
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
        self.name = self._validate_name(self.name)
        self.interpolator = self._validate_interpolator(self.interpolator)

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

    @classmethod
    def from_wells(
        cls,
        *,
        name: str,
        wells: Iterable["VerticalWell"],
        interpolator: BaseInterpolator,
        store_picks: bool = True,
    ) -> "Horizon":

        xy = []
        z = []

        for well in wells:
            if name not in well.tops:
                raise ValueError(f"Well '{well.name}' does not have a top for horizon '{name}'.")

            xy.append(well.xy)
            z.append(well.tops[name])

        return cls(
            name=name,
            interpolator=interpolator,
            xy=np.asarray(xy, dtype=float),
            z=np.asarray(z, dtype=float),
            store_picks=store_picks,
        )

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
    
    def intersect(self, well: VerticalWell) -> float:
        x, y = well.xy
        return float(self.sample([[x, y]])[0])

    def show(
        self,
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        view: Literal["3d", "2d"] = "3d",
    ) -> None:
        if view == "3d":
            self.show3d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy)
        elif view == "2d":
            self.show2d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy)
        else:
            raise ValueError(f"Invalid view: {view!r}. Must be '3d' or '2d'.")
        
    def show3d(
        self,
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        color: Any | None = 'tan',
        scalars: bool = True,
        cmap: Optional[str] = 'turbo',
    ):
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_horizon(self, x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy, color=color, scalars=scalars, cmap=cmap)
        viewer.show()

    def show2d(
        self,
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        cmap: str = "turbo",
        show_contours: bool = True,
        contour_levels: int = 10,
        **kwargs,
    ):
        """
        Show horizon in 2D matplotlib view.
        
        Parameters
        ----------
        x : np.ndarray, optional
            1D array of x coordinates.
        y : np.ndarray, optional
            1D array of y coordinates.
        xlim : tuple[float, float], optional
            X-axis limits (min, max).
        ylim : tuple[float, float], optional
            Y-axis limits (min, max).
        ni : int, optional
            Number of points in x direction.
        nj : int, optional
            Number of points in y direction.
        dx : float, optional
            Spacing in x direction.
        dy : float, optional
            Spacing in y direction.
        cmap : str
            Colormap name (default: "viridis").
        show_contours : bool
            Whether to show contour lines (default: True).
        contour_levels : int
            Number of contour levels (default: 10).
        **kwargs
            Additional kwargs passed to the viewer.
        """
        from ..viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer

        viewer = Matplotlib2DViewer()
        viewer.add_horizon(
            self, 
            x=x, y=y, 
            xlim=xlim, ylim=ylim, 
            ni=ni, nj=nj, 
            dx=dx, dy=dy,
            cmap=cmap,
            show_contours=show_contours,
            contour_levels=contour_levels,
            **kwargs
        )
        viewer.show()

    def _validate_interpolator(self, interpolator: Any) -> BaseInterpolator:
        if not isinstance(interpolator, BaseInterpolator):
            raise TypeError(f"Horizon interpolator must be a `BaseInterpolator` instance. Got {type(interpolator)}")
        
        if not hasattr(interpolator, 'allowed_dims'):
            raise TypeError(f"Horizon interpolator must have an 'allowed_dims' attribute. Got {type(interpolator)}")
        
        if interpolator.is_allowed_dim(2) is False:
            raise TypeError(
                f"Horizon interpolator must support 2D coordinates (x,y). "
                f"But {interpolator.allowed_dims} were allowed.")
        return interpolator
    
    def _validate_name(self, name: Any) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError(f"Horizon name must be a non-empty string. Got {name!r}")
        return name