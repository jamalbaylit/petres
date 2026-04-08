from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike


from ..interpolators.base import BaseInterpolator
from ..models.wells import VerticalWell
from .zone import Zone


@dataclass
class Horizon:
    """Continuous horizon defined from scattered picks and an interpolator.

    Parameters
    ----------
    name : str
        Horizon identifier used in viewers and derived objects.
    interpolator : BaseInterpolator
        Fitted in ``__post_init__`` on the provided ``xy``/``depth`` picks.
        Must accept 2D inputs.
    xy : ndarray with dimensions (n, 2)
        XY coordinates for the picked horizon points.
    depth : ndarray with dimensions (n,)
        Depth values for each pick. Must align with the rows of ``xy``.
    store_picks : bool, default True
        Whether to retain the raw picks after fitting. Set to ``False`` to
        minimize memory once the interpolator is trained.

    Notes
    -----
    The dataclass-generated ``__init__`` delegates validation and fitting to
    ``__post_init__``. Use :meth:`from_wells` to build horizons from well tops.
    """
    name: str
    interpolator: BaseInterpolator
    xy: ArrayLike = field(repr=False)
    depth: ArrayLike = field(repr=False)
    store_picks: bool = True  

    def __post_init__(self) -> None:
        """Validate inputs, coerce arrays, and fit the interpolator.

        Raises
        ------
        ValueError
            If ``xy`` does not have dimensions ``(n, 2)`` or ``depth`` does
            not match the number of picks.
        TypeError
            If the interpolator is not a ``BaseInterpolator`` instance or does
            not support 2D coordinates.
        """
        self.name = self._validate_name(self.name)
        self.interpolator = self._validate_interpolator(self.interpolator)

        self.xy = np.asarray(self.xy, dtype=float)
        self.depth = np.asarray(self.depth, dtype=float)

        if self.xy.ndim != 2 or self.xy.shape[1] != 2:
            raise ValueError(f"Horizon '{self.name}': xy must be shape (n,2). Got {self.xy.shape}")
        if self.depth.ndim != 1 or self.depth.shape[0] != self.xy.shape[0]:
            raise ValueError(f"Horizon '{self.name}': `depth` must be shape (n,) matching xy. Got {self.depth.shape}")

        # Fit interpolator; BaseInterpolator validates + sets dim_
        self.interpolator.fit(self.xy, self.depth)

        if not self.store_picks:
            # free memory if user doesn't need provenance
            self.xy = np.empty((0, 2), dtype=float)
            self.depth = np.empty((0,), dtype=float)

    @classmethod
    def from_wells(
        cls,
        *,
        name: str,
        wells: Iterable[VerticalWell],
        interpolator: BaseInterpolator,
        store_picks: bool = True,
    ) -> Horizon:
        """Construct a horizon from well tops.

        Parameters
        ----------
        name : str
            Horizon name to extract from each well's ``tops`` mapping.
        wells : Iterable[VerticalWell]
            Wells providing XY positions and horizon tops.
        interpolator : BaseInterpolator
            Interpolator instance to fit on the aggregated picks.
        store_picks : bool, default True
            Whether to keep the picks after fitting.

        Returns
        -------
        Horizon
            Horizon fitted to the provided well tops.

        Raises
        ------
        ValueError
            If any well is missing the requested horizon top.

        Examples
        --------
        >>> horizon = Horizon.from_wells(
        ...     name="TopReservoir",
        ...     wells=[well_a, well_b],
        ...     interpolator=my_rbf,
        ... )
        """

        xy = []
        depth = []

        for well in wells:
            if name not in well.tops:
                raise ValueError(f"Well '{well.name}' does not have a top for horizon '{name}'.")

            xy.append(well.xy)
            depth.append(well.tops[name])

        return cls(
            name=name,
            interpolator=interpolator,
            xy=np.asarray(xy, dtype=float),
            depth=np.asarray(depth, dtype=float),
            store_picks=store_picks,
        )

    def to_zone(self, name: str, depth: float) -> Zone:

        """Create a zone by shifting this horizon by a constant depth.

        Parameters
        ----------
        name : str
            Name of the generated zone.
        depth : float
            Vertical shift applied to derive the second horizon. Positive values
            move the second horizon deeper (assuming depth increases downward).

        Returns
        -------
        Zone
            Zone composed of this horizon and the shifted counterpart.

        Raises
        ------
        ValueError
            If ``depth`` is zero or picks were not retained (``store_picks=False``).

        Examples
        --------
        >>> gross = horizon.to_zone(name="Gross", depth=25.0)
        >>> gross.top is horizon
        True
        """
        if depth == 0:
            raise ValueError("'depth' cannot be zero.")

        if self.xy.size == 0:
            raise ValueError(
                "Cannot generate second horizon because picks were not stored "
                "(store_picks=False)."
            )

        new_depth = self.depth + depth

        new_interp = type(self.interpolator)()

        other = Horizon(
            name=f"{self.name}_shifted",
            interpolator=new_interp,
            xy=self.xy.copy(),
            depth=new_depth,
            store_picks=self.store_picks,
        )

        # Determine top/base based on relative depth
        if depth > 0:
            # shifted horizon is deeper
            return Zone(name=name, top=self, base=other)
        else:
            return Zone(name=name, top=other, base=self)

    def sample(self, xy: ArrayLike) -> np.ndarray:
        """Evaluate the horizon depth at arbitrary XY locations.

        Parameters
        ----------
        xy : array-like with dimensions (n, 2)
            Points containing x and y coordinates.

        Returns
        -------
        ndarray
            Depth values with length ``n``.

        Raises
        ------
        ValueError
            If `xy` is not a 2D array with two columns.

        Examples
        --------
        >>> xy = np.array([[0.0, 0.0], [10.0, 5.0]])
        >>> horizon.sample(xy)
        array([1234.5, 1236.8])
        """
        xy = np.asarray(xy, dtype=float)
        if xy.ndim != 2 or xy.shape[1] != 2:
            raise ValueError(f"Horizon '{self.name}': sample expects xy shape (n,2). Got {xy.shape}")
        return self.interpolator.predict(xy)

    def to_grid(self, x: ArrayLike, y: ArrayLike) -> np.ndarray:
        """Resample the horizon onto a rectilinear grid.

        Parameters
        ----------
        x : array-like
            1D x-vertices.
        y : array-like
            1D y-vertices.

        Returns
        -------
        ndarray
            Depth array with dimensions ``(len(y), len(x))`` matching
            ``meshgrid(y, x)`` order.

        Examples
        --------
        >>> x = np.linspace(0, 100, 11)
        >>> y = np.linspace(0, 50, 6)
        >>> depth_grid = horizon.to_grid(x, y)
        """
        x = np.asarray(x, dtype=float).ravel()
        y = np.asarray(y, dtype=float).ravel()
        xx, yy = np.meshgrid(x, y)
        pts = np.column_stack([xx.ravel(), yy.ravel()])
        return self.sample(pts).reshape(y.size, x.size)
    
    def intersect(self, well: VerticalWell) -> float:
        """Compute the depth where the horizon intersects a vertical well.

        Parameters
        ----------
        well : VerticalWell
            Well instance providing XY coordinates.

        Returns
        -------
        float
            Depth value at the well location.

        Examples
        --------
        >>> horizon.intersect(well)
        1530.2
        """
        x, y = well.xy
        return float(self.sample([[x, y]])[0])

    def show(
        self,
        *,
        x: ArrayLike | None = None,
        y: ArrayLike | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        view: Literal["3d", "2d"] = "3d",
    ) -> None:
        """Render the horizon in either 3D or 2D.

        Dispatches to `show3d` or `show2d` based on `view`, passing through any
        grid specification arguments.

        Parameters
        ----------
        x : array-like or None, optional
            1D x-vertices. Mutually exclusive with `xlim`.
        y : array-like or None, optional
            1D y-vertices. Mutually exclusive with `ylim`.
        xlim : tuple[float, float] or None, optional
            Inclusive x-limits used to generate vertices when `x` is not given.
        ylim : tuple[float, float] or None, optional
            Inclusive y-limits used to generate vertices when `y` is not given.
        ni : int or None, optional
            Number of cells along x when using `xlim`. Must be >= 1.
        nj : int or None, optional
            Number of cells along y when using `ylim`. Must be >= 1.
        dx : float or None, optional
            Cell size along x when using `xlim`. Mutually exclusive with `ni`.
        dy : float or None, optional
            Cell size along y when using `ylim`. Mutually exclusive with `nj`.
        view : {'3d', '2d'}, default '3d'
            Target visualization backend. Use '3d' for PyVista, '2d' for Matplotlib.

        Raises
        ------
        ValueError
            If `view` is not one of {'3d', '2d'}.

        Examples
        --------
        >>> horizon.show()
        >>> horizon.show(view="2d", x=[0, 10], y=[0, 10])
        """
        view = view.strip().lower()
        if view == "3d":
            self.show3d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy)
        elif view == "2d":
            self.show2d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy)
        else:
            raise ValueError(f"Invalid view: {view!r}. Must be '3d' or '2d'.")
        
    def show3d(
        self,
        *,
        x: ArrayLike | None = None,
        y: ArrayLike | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        color: Any | None = "tan",
        scalars: bool = True,
        cmap: str | None = "turbo",
        title: str | Literal["auto"] | None = "auto", 
        z_scale: float = 1.0,
    ) -> None:
        """Render the horizon in an interactive 3D PyVista scene.

        Samples the interpolated surface on the provided grid and adds it to a
        `PyVista3DViewer`, coloring by depth.

        Parameters
        ----------
        x, y : array-like or None, optional
            1D vertex arrays. Mutually exclusive with `xlim`/`ylim`.
        xlim, ylim : tuple[float, float] or None, optional
            Bounds used to generate vertices when `x` or `y` are not supplied.
        ni, nj : int or None, optional
            Number of cells along x/y when using bounds. Must be >= 1.
        dx, dy : float or None, optional
            Cell size along x/y when using bounds. Mutually exclusive with `ni`/`nj`.
        color : Any or None, default 'tan'
            Solid color for the surface when `scalars` is False; otherwise used as
            edge/mesh color by the backend.
        scalars : bool, default True
            Whether to color by depth values.
        cmap : str or None, default 'turbo'
            Colormap name applied when `scalars` is True.
        title : str or 'auto', default 'auto'
            Window title; ``'auto'`` uses the property name.
        z_scale : float, default 1.0
            Scale factor for the z-axis to exaggerate vertical relief.

        Examples
        --------
        >>> horizon.show3d(x=[0, 100], y=[0, 100], ni=50, nj=50, cmap="viridis")
        """
        from ..viewers.viewer3d.pyvista.theme import PyVista3DViewerTheme
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        if not np.isfinite(z_scale) or z_scale <= 0:
            raise ValueError("z_scale must be a positive finite value.")
        theme = PyVista3DViewerTheme(scale=(1.0, 1.0, float(z_scale)))
        viewer = PyVista3DViewer(theme=theme)
        viewer.add_horizon(
            self, x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy, 
            color=color, 
            scalars=scalars, 
            cmap=cmap,
            show_colorbar=True,
            colorbar_title='Depth',
        )
        title = f"Horizon: {self.name}" if title == 'auto' else str(title)
        viewer.show(title=title)

    def show2d(
        self,
        *,
        x: ArrayLike | None = None,
        y: ArrayLike | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        cmap: str = "turbo",
        show_contours: bool = True,
        contour_levels: int = 10,
        aspect: Literal["auto", "equal"] = "auto",
        title: str | Literal["auto"] | None = "auto",
        **kwargs: Any,
    ) -> None:
        """Render the horizon as a 2D Matplotlib map.

        Interpolates the surface on a regular grid and displays it with optional
        contours.

        Parameters
        ----------
        x, y : array-like or None, optional
            1D vertex arrays. Mutually exclusive with `xlim`/`ylim`.
        xlim, ylim : tuple[float, float] or None, optional
            Bounds used to generate vertices when `x` or `y` are not supplied.
        ni, nj : int or None, optional
            Number of cells along x/y when using bounds. Must be >= 1.
        dx, dy : float or None, optional
            Cell size along x/y when using bounds. Mutually exclusive with `ni`/`nj`.
        cmap : str, default "turbo"
            Colormap used for the surface.
        show_contours : bool, default True
            Whether to overlay contour lines.
        contour_levels : int, default 10
            Number of contour levels.
        aspect : {'auto', 'equal'}, default 'auto'
            Axes aspect ratio.
        title : str or 'auto', default 'auto'
            Window title; ``'auto'`` uses the property name.
        **kwargs
            Additional keyword arguments forwarded to the Matplotlib surface helper.

        Examples
        --------
        >>> horizon.show2d(xlim=(0, 500), ylim=(0, 500), ni=100, nj=100, cmap="magma")
        """
        from ..viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer
        from ..viewers.viewer2d.matplotlib.theme import Matplotlib2DViewerTheme
        
        viewer = Matplotlib2DViewer(theme = Matplotlib2DViewerTheme(aspect=aspect))
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
        title = f"Horizon: {self.name}" if title == 'auto' else str(title)
        viewer.show(title=title)

    def _validate_interpolator(self, interpolator: Any) -> BaseInterpolator:
        """Validate interpolator type and dimensional support.

        Parameters
        ----------
        interpolator : Any
            Candidate interpolator instance.

        Returns
        -------
        BaseInterpolator
            The validated interpolator.

        Raises
        ------
        TypeError
            If the interpolator is not a ``BaseInterpolator`` or lacks the
            required ``allowed_dims``/``is_allowed_dim`` interface.
        """
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
        """Validate and normalize the horizon name.

        Parameters
        ----------
        name : Any
            Candidate horizon name.

        Returns
        -------
        str
            Validated non-empty string name.
        """
        if not isinstance(name, str) or not name:
            raise ValueError(f"Horizon name must be a non-empty string. Got {name!r}")
        return name