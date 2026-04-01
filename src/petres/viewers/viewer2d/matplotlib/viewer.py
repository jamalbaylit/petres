from __future__ import annotations

from typing import Any, Literal, Self

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .layers.boundary import _add_boundary_polygon
from .layers.surface import _add_surface
from .layers.zone import _add_zone
from .theme import Matplotlib2DViewerTheme
from .._core.base import Base2DViewer
from ....grids.sampling._vertices import _resolve_xy_vertices
from ....models.boundary import BoundaryPolygon
from ....models.horizon import Horizon
from ....models.zone import Zone


ColorLike = (
    str
    | tuple[float, float, float]
    | tuple[float, float, float, float]
)


class Matplotlib2DViewer(Base2DViewer):
    """Render 2D reservoir objects with Matplotlib.

    This viewer manages a Matplotlib figure/axes pair, applies a reusable visual
    theme, and provides convenience methods to plot horizons, zones, and boundary
    polygons on a common 2D canvas.
    """

    def __init__(
        self,
        fig: Figure | None = None,
        ax: Axes | None = None,
        theme: Matplotlib2DViewerTheme | None = None,
    ) -> None:
        """Initialize a Matplotlib 2D viewer.

        Parameters
        ----------
        fig : Figure or None, default=None
            Figure instance to use. If provided without ``ax``, a new subplot is
            created on this figure.
        ax : Axes or None, default=None
            Axes instance to use. If provided without ``fig``, the corresponding
            ``ax.figure`` is used automatically.
        theme : Matplotlib2DViewerTheme or None, default=None
            Theme configuration controlling layout and styling. When ``None``, the
            default ``Matplotlib2DViewerTheme`` is used.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If both ``fig`` and ``ax`` are provided but ``ax`` does not belong to
            ``fig``.
        """
        self.set_theme(theme or Matplotlib2DViewerTheme())

        if fig is not None and ax is not None:
            if ax.figure is not fig:
                raise ValueError("`ax` does not belong to the provided `fig`.")
            self.fig = fig
            self.ax = ax
        elif ax is not None:
            self.ax = ax
            self.fig = ax.figure
        elif fig is not None:
            self.fig = fig
            self.ax = fig.add_subplot(111)
        else:
            self.fig, self.ax = plt.subplots(
                figsize=self.theme.figure_size,
                dpi=self.theme.dpi,
                constrained_layout=self.theme.constrained_layout,
            )

    def set_theme(self, theme: Matplotlib2DViewerTheme) -> None:
        """Set the active viewer theme.

        Parameters
        ----------
        theme : Matplotlib2DViewerTheme
            Theme object containing visual settings such as figure size, axis
            labels, and grid behavior.

        Returns
        -------
        None
        """
        self.theme = theme

    def apply_theme(self) -> None:
        """Apply the active theme values to the current axes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        ax = self.ax
        theme = self.theme

        ax.set_facecolor(theme.background)
        ax.set_aspect(theme.aspect, adjustable="box")

        if theme.grid:
            ax.grid(
                True,
                alpha=theme.grid_alpha,
                linestyle=theme.grid_linestyle,
                linewidth=theme.grid_linewidth,
            )
        else:
            ax.grid(False)

        if theme.show_labels:
            ax.set_xlabel(theme.xlabel)
            ax.set_ylabel(theme.ylabel)

        ax.tick_params(labelsize=theme.tick_labelsize)

        if theme.hide_top_right_spines:
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)

    def show(self, *, title: str | None = None) -> None:
        """Autoscale, style, and display the current figure.

        Parameters
        ----------
        title : str or None, default=None
            Optional title text shown above the axes.

        Returns
        -------
        None
        """
        self.ax.relim()
        self.ax.autoscale_view()
        if title:
            self.ax.set_title(str(title), fontsize=self.theme.title_fontsize, pad=10)
        self.apply_theme()
        plt.show()

    def add_horizon(
        self,
        horizon: Horizon,
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        **kwargs: Any,
    ) -> Self:
        """Add a horizon map to the 2D axes.

        The method resolves/derives 1D vertex coordinates, samples the horizon on
        the resulting grid, and forwards the scalar map to the surface layer.

        Parameters
        ----------
        horizon : Horizon
            Horizon instance to render.
        x : ndarray or None, default=None
            1D x-vertex coordinates. Mutually exclusive with ``xlim``/``ni``/``dx``.
        y : ndarray or None, default=None
            1D y-vertex coordinates. Mutually exclusive with ``ylim``/``nj``/``dy``.
        xlim : tuple[float, float] or None, default=None
            Inclusive x-bounds used to generate vertices when ``x`` is not provided.
        ylim : tuple[float, float] or None, default=None
            Inclusive y-bounds used to generate vertices when ``y`` is not provided.
        ni : int or None, default=None
            Number of x-direction cells used with ``xlim``.
        nj : int or None, default=None
            Number of y-direction cells used with ``ylim``.
        dx : float or None, default=None
            X cell size used with ``xlim`` as an alternative to ``ni``.
        dy : float or None, default=None
            Y cell size used with ``ylim`` as an alternative to ``nj``.
        **kwargs
            Additional keyword arguments forwarded to the surface plotting helper.

        Returns
        -------
        Matplotlib2DViewer
            The viewer instance (for chaining).

        Raises
        ------
        ValueError
            If vertex resolution arguments are inconsistent.

        Examples
        --------
        >>> viewer = Matplotlib2DViewer()
        >>> viewer.add_horizon(horizon, xlim=(0, 500), ylim=(0, 400), ni=100, nj=80, cmap="viridis").show()
        """
        x, y = _resolve_xy_vertices(
            x=x,
            y=y,
            xlim=xlim,
            ylim=ylim,
            ni=ni,
            nj=nj,
            dx=dx,
            dy=dy,
        )
        scalars = horizon.to_grid(x, y)
        _add_surface(
            self.ax,
            scalars,
            x=x,
            y=y,
            **kwargs,
        )
        return self

    def add_zone(
        self,
        zone: Zone,
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
        **kwargs: Any,
    ) -> Self:
        """Add a zone scalar map to the 2D axes.

        The method samples the zone top/base surfaces on a resolved grid and plots
        either top, base, or absolute thickness values.

        Parameters
        ----------
        zone : Zone
            Zone instance to render.
        x : ndarray or None, default=None
            1D x-vertex coordinates. Mutually exclusive with ``xlim``/``ni``/``dx``.
        y : ndarray or None, default=None
            1D y-vertex coordinates. Mutually exclusive with ``ylim``/``nj``/``dy``.
        xlim : tuple[float, float] or None, default=None
            Inclusive x-bounds used to generate vertices when ``x`` is not provided.
        ylim : tuple[float, float] or None, default=None
            Inclusive y-bounds used to generate vertices when ``y`` is not provided.
        ni : int or None, default=None
            Number of x-direction cells used with ``xlim``.
        nj : int or None, default=None
            Number of y-direction cells used with ``ylim``.
        dx : float or None, default=None
            X cell size used with ``xlim`` as an alternative to ``ni``.
        dy : float or None, default=None
            Y cell size used with ``ylim`` as an alternative to ``nj``.
        mode : {'top', 'base', 'thickness'}, default='thickness'
            Which scalar field to plot.
        **kwargs
            Additional keyword arguments forwarded to the surface plotting helper.

        Returns
        -------
        Matplotlib2DViewer
            The viewer instance (for chaining).

        Raises
        ------
        ValueError
            If ``mode`` is not one of ``'top'``, ``'base'``, or ``'thickness'``.

        Examples
        --------
        >>> Matplotlib2DViewer().add_zone(zone, x=[0, 50], y=[0, 50], mode="top", cmap="cividis").show()
        """
        x, y = _resolve_xy_vertices(
            x=x,
            y=y,
            xlim=xlim,
            ylim=ylim,
            ni=ni,
            nj=nj,
            dx=dx,
            dy=dy,
        )
        top, base = zone.to_grid(x, y)
        
        if mode == "top":
            scalars = top
        elif mode == "base":
            scalars = base
        elif mode == "thickness":
            scalars = np.abs(base - top)
        else:
            raise ValueError(f"Invalid mode: {mode!r}. Must be 'top', 'base', or 'thickness'.")

        _add_surface(
            self.ax,
            scalars=scalars,
            x=x,
            y=y,
            **kwargs,
        )
        return self

    def add_boundary_polygon(
        self,
        boundary: BoundaryPolygon,
        *,
        facecolor: ColorLike = "#7ec8e3",
        edgecolor: ColorLike = "#1f2937",
        linewidth: float = 1.8,
        alpha: float = 0.30,
        show_fill: bool = True,
        show_vertices: bool = False,
        vertex_color: ColorLike | None = None,
        vertex_size: float = 24.0,
        show_label: bool = True,
        label: str | None = None,
        label_fontsize: float = 10.0,
        label_box: bool = True,
        pad_ratio: float | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Add a boundary polygon overlay to the 2D axes.

        Parameters
        ----------
        boundary : BoundaryPolygon
            Polygon to draw.
        facecolor : str or tuple[float, float, float] or tuple[float, float, float, float], default='#7ec8e3'
            Fill color for the polygon.
        edgecolor : str or tuple[float, float, float] or tuple[float, float, float, float], default='#1f2937'
            Edge color.
        linewidth : float, default=1.8
            Boundary line width.
        alpha : float, default=0.30
            Fill opacity (0–1).
        show_fill : bool, default=True
            Whether to fill the polygon.
        show_vertices : bool, default=False
            Whether to show vertex markers.
        vertex_color : str or tuple[float, float, float] or tuple[float, float, float, float] or None, default=None
            Color for vertex markers; defaults to `edgecolor`.
        vertex_size : float, default=24.0
            Marker size for vertices.
        show_label : bool, default=True
            Whether to render the polygon name/label.
        label : str or None, default=None
            Custom label text; defaults to `boundary.name`.
        label_fontsize : float, default=10.0
            Font size for the label.
        label_box : bool, default=True
            Whether to draw a small background box behind the label.
        pad_ratio : float or None, default=None
            Padding fraction applied to axis limits; defaults to theme margins.
        **kwargs
            Additional keyword arguments forwarded to the patch helper.

        Returns
        -------
        Matplotlib2DViewer
            The viewer instance (for chaining).

        Examples
        --------
        >>> viewer = Matplotlib2DViewer()
        >>> viewer.add_boundary_polygon(boundary, show_vertices=True, vertex_size=30).show()
        """
        _add_boundary_polygon(
            self.ax,
            boundary,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            show_fill=show_fill,
            show_vertices=show_vertices,
            vertex_color=edgecolor if vertex_color is None else vertex_color,
            vertex_size=vertex_size,
            show_label=show_label,
            label=label,
            label_fontsize=label_fontsize,
            label_box=label_box,
            pad_ratio=self.theme.margins if pad_ratio is None else pad_ratio,
            **kwargs,
        )
        return self