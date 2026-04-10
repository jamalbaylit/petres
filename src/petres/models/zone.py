from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal
import numpy as np

from .wells import VerticalWell, _validate_well_sequence

@dataclass(frozen=True)
class Zone:
    """A stratigraphic interval bounded by a top and base horizon.

    Parameters
    ----------
    name : str
        Identifier for the zone.
    top : Horizon
        Upper horizon surface.
    base : Horizon
        Lower horizon surface.
    levels : tuple[float, ...], default (0.0, 1.0)
        Normalized internal layer interfaces in the range [0, 1]. The default
        represents a single layer with no subdivision.
    """

    name: str
    top: "Horizon"
    base: "Horizon"
    levels: tuple[float, ...] = (0.0, 1.0)  # default: single layer

    @property
    def n_layers(self) -> int:
        """Return the number of layers defined by `levels`."""
        return len(self.levels) - 1
    
    def thickness(self, xy: np.ndarray) -> np.ndarray:
        """
        Compute zone thickness at the given XY locations.

        Parameters
        ----------
        xy : ndarray
            Points of shape (n, 2) containing x and y coordinates.

        Returns
        -------
        ndarray
            Thickness values (base minus top) of shape (n,).

        Examples
        --------
        >>> xy = np.array([[0, 0], [50, 20]])
        >>> zone.thickness(xy)
        array([30.1, 29.8])
        """
        return self.base.sample(xy) - self.top.sample(xy)
    
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
        wells: Sequence[VerticalWell] | VerticalWell | None = None,

    ) -> None:
        """
        Render the zone in 3D or 2D.

        Dispatches to `show3d` or `show2d` depending on `view`, passing through
        any grid specification arguments.

        Parameters
        ----------
        x, y : ndarray or None, default None
            1D vertex arrays. Mutually exclusive with `xlim`/`ylim`.
        xlim, ylim : tuple[float, float] or None, default None
            Bounds used to generate vertices when `x` or `y` are not supplied.
        ni, nj : int or None, default None
            Number of cells along x/y when using bounds. Must be >= 1.
        dx, dy : float or None, default None
            Cell size along x/y when using bounds. Mutually exclusive with `ni`/`nj`.
        view : {'3d', '2d'}, default '3d'
            Target visualization backend.

        Raises
        ------
        ValueError
            If `view` is not one of {'3d', '2d'}.

        Examples
        --------
        >>> zone.show()
        >>> zone.show(view="2d", xlim=(0, 500), ylim=(0, 500), ni=100, nj=100)
        """
        view = view.strip().lower()
        if view == "3d":
            self.show3d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy, wells=wells)
        elif view == "2d":
            self.show2d(x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy, wells=wells)
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
        z_scale: float = 1.0,
        title: str | Literal["auto"] | None = "auto",
        color: Any | None = 'gray',
        show_layers: bool = True,
        show_edges: bool = True,
        wells: Sequence[VerticalWell] | VerticalWell | None = None,
    ) -> None:
        """
        Render the zone in an interactive 3D PyVista scene.

        Adds the zone’s top/base surfaces and optional layer slices to a
        `PyVista3DViewer`.

        Parameters
        ----------
        x, y : ndarray or None, default None
            1D vertex arrays. Mutually exclusive with `xlim`/`ylim`.
        xlim, ylim : tuple[float, float] or None, default None
            Bounds used to generate vertices when `x` or `y` are not supplied.
        ni, nj : int or None, default None
            Number of cells along x/y when using bounds. Must be >= 1.
        dx, dy : float or None, default None
            Cell size along x/y when using bounds. Mutually exclusive with `ni`/`nj`.
        color : Any or None, default 'gray'
            Solid color for the zone surfaces.
        show_layers : bool, default True
            Whether to render internal layers derived from `levels`.
        show_edges : bool, default True
            Whether to draw mesh edges.
        title : str or 'auto', default 'auto'
            Window title; ``'auto'`` uses the property name.
        z_scale : float, default 1.0
            Scale factor for the z-axis.
        wells : VerticalWell or Sequence[VerticalWell] or None, optional
            Well(s) to plot on top of the grid. Can be a single VerticalWell or a sequence of them. If ``None``, no wells are plotted.

        Examples
        --------
        >>> zone.show3d(x=[0, 100], y=[0, 50], ni=50, nj=25, color="lightgray")
        """
        from ..viewers.viewer3d.pyvista.theme import PyVista3DViewerTheme
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        if not np.isfinite(z_scale) or z_scale <= 0:
            raise ValueError("z_scale must be a positive finite value.")
        theme = PyVista3DViewerTheme(scale=(1.0, 1.0, float(z_scale)))
        viewer = PyVista3DViewer(theme=theme)
        
        title = self._get_plot_title(title)

        viewer.add_zone(
            self, x=x, y=y, xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy, 
            color=color,
            show_layers=show_layers,
            show_edges=show_edges,
        )
        if wells is not None:
            viewer.add_wells(_validate_well_sequence(wells))
        viewer.show(title=title)

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
        mode: Literal["top", "base", "thickness"] = "thickness",
        cmap: str = "turbo",
        show_contours: bool = True,
        contour_levels: int = 10,
        aspect: Literal["auto", "equal"] = "auto",
        title: str | None = 'auto',
        wells: Sequence[VerticalWell] | VerticalWell | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Render the zone as 2D maps of top, base, or thickness.

        Samples the top/base horizons on a rectilinear grid and plots the chosen
        scalar field.

        Parameters
        ----------
        x, y : ndarray or None, default None
            1D vertex arrays. Mutually exclusive with `xlim`/`ylim`.
        xlim, ylim : tuple[float, float] or None, default None
            Bounds used to generate vertices when `x` or `y` are not supplied.
        ni, nj : int or None, default None
            Number of cells along x/y when using bounds. Must be >= 1.
        dx, dy : float or None, default None
            Cell size along x/y when using bounds. Mutually exclusive with `ni`/`nj`.
        mode : {'top', 'base', 'thickness'}, default 'thickness'
            Which scalar to plot.
        cmap : str, default 'turbo'
            Colormap used for the surface.
        show_contours : bool, default True
            Whether to overlay contour lines.
        contour_levels : int, default 10
            Number of contour levels.
        aspect : {'auto', 'equal'}, default 'auto'
            Axes aspect ratio.
        title : str or None, default 'auto'
            Plot title; when 'auto' uses the zone name.
        wells : VerticalWell or Sequence[VerticalWell] or None, optional
            Well(s) to plot on top of the grid. Can be a single VerticalWell or a sequence of them. If ``None``, no wells are plotted.

        **kwargs
            Additional keyword arguments forwarded to the Matplotlib surface helper.

        Examples
        --------
        >>> zone.show2d(mode="top", xlim=(0, 400), ylim=(0, 300), ni=80, nj=60, cmap="cividis")
        """
        from ..viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer
        from ..viewers.viewer2d.matplotlib.theme import Matplotlib2DViewerTheme
        
        title = self._get_plot_title(title)
        
        viewer = Matplotlib2DViewer(theme = Matplotlib2DViewerTheme(aspect=aspect))
        viewer.add_zone(
            self, 
            x=x, y=y, 
            xlim=xlim, ylim=ylim, 
            ni=ni, nj=nj, 
            dx=dx, dy=dy,
            mode=mode,
            cmap=cmap,
            show_contours=show_contours,
            contour_levels=contour_levels,
            **kwargs
        )
        if wells is not None:
            viewer.add_wells(_validate_well_sequence(wells))
        viewer.show(title=title)

    def _get_plot_title(self, title: str | Literal["auto"] | None) -> str | None:
        if title == 'auto':
            return f"Zone: {self.name}"
        elif title is not None:
            return str(title)
        else:
            return None
        
        
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
        nk : int or None, default None
            Number of layers divided equally. Must be >= 2.
        fractions : Sequence[float] or None, default None
            Relative layer thicknesses (positive). Normalized to sum to 1.
            Example: ``[0.1, 0.2, 0.7]`` -> levels ``[0, 0.1, 0.3, 1.0]``.
        levels : Sequence[float] or None, default None
            Normalized interface levels in [0, 1], strictly increasing,
            starting at 0 and ending at 1.
            Example: ``[0, 0.3, 1]`` -> 2 layers.
 
        Returns
        -------
        Zone
            New Zone instance with updated `levels`.

        Raises
        ------
        ValueError
            If more than one of ``nk``, ``fractions``, or ``levels`` is
            provided, or if inputs violate monotonicity/validity rules.
        TypeError
            If ``nk`` is not an integer when supplied.
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
        """Validate normalized layer interfaces.

        Parameters
        ----------
        levels : Sequence[float]
            Candidate interface levels in [0, 1], starting at 0 and ending at 1.

        Returns
        -------
        tuple[float, ...]
            Strictly increasing normalized levels with exact endpoints (0.0, 1.0).
        """
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
        """Convert relative layer fractions to normalized interfaces.

        Parameters
        ----------
        fractions : Sequence[float]
            Positive layer fractions to normalize.

        Returns
        -------
        tuple[float, ...]
            Strictly increasing levels from 0.0 to 1.0.
        """
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
        """Generate evenly spaced interfaces from a layer count.

        Parameters
        ----------
        nk : int
            Number of layers, with the constraint `nk >= 2`.

        Returns
        -------
        tuple[float, ...]
            Equally spaced normalized levels in [0, 1].
        """
        if not isinstance(nk, int):
            raise TypeError("'nk' must be an int.")
        if not nk >= 2:
            raise ValueError("'nk' must be >= 2.")
    
        lv = np.linspace(0.0, 1.0, nk + 1, dtype=float)
        return self._validate_levels(lv)

    def to_grid(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Sample top and base horizons on a rectilinear grid.

        Parameters
        ----------
        x : ndarray
            1D x-vertices.
        y : ndarray
            1D y-vertices.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            Tuple `(top_z, base_z)` each of shape (len(y), len(x)).

        Examples
        --------
        >>> x = np.linspace(0, 200, 41)
        >>> y = np.linspace(0, 100, 21)
        >>> top_z, base_z = zone.to_grid(x, y)
        """
        top_z = self.top.to_grid(x, y)
        base_z = self.base.to_grid(x, y)
        return top_z, base_z
    
