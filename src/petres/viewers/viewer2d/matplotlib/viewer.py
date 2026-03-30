from __future__ import annotations

from typing import Any, Self
import matplotlib

# Use non-interactive backend to allow headless environments (e.g., CI)
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from .layers.boundary import _add_boundary_polygon
from .layers.horizon import _add_horizon
from .layers.zone import _add_zone
from .theme import Matplotlib2DViewerTheme
from .._core.base import Base2DViewer
from ....models.horizon import Horizon
from ....models.zone import Zone
from ....models.boundary import BoundaryPolygon
from ....grids.sampling._vertices import _resolve_xy_vertices


class Matplotlib2DViewer(Base2DViewer):
    """
    Matplotlib-based 2D viewer for geological surfaces.
    """
    
    theme: Matplotlib2DViewerTheme
    fig: Figure
    ax: Axes
    
    def __init__(
        self, 
        fig: Figure | None = None,
        ax: Axes | None = None,
        theme: Matplotlib2DViewerTheme | None = None,
    ):
        self.set_theme(theme or Matplotlib2DViewerTheme())
        
        if fig is not None and ax is not None:
            self.fig = fig
            self.ax = ax
        elif fig is not None:
            self.fig = fig
            self.ax = fig.gca()
        else:
            self.fig, self.ax = plt.subplots(
                figsize=self.theme.figure_size,
                dpi=self.theme.dpi
            )
    
    def set_theme(self, theme: Matplotlib2DViewerTheme) -> None:
        """Apply theme settings to the viewer."""
        assert isinstance(theme, Matplotlib2DViewerTheme), "`theme` must be a Matplotlib2DViewerTheme instance."
        self.theme = theme
    
    def apply_theme(self) -> None:
        """Apply current theme to the axes."""
        ax = self.ax
        
        # Background
        ax.set_facecolor(self.theme.background)
        
        # Grid
        if self.theme.grid:
            ax.grid(True, alpha=self.theme.grid_alpha)
        else:
            ax.grid(False)
        
        # Labels
        if self.theme.show_labels:
            ax.set_xlabel(self.theme.xlabel)
            ax.set_ylabel(self.theme.ylabel)
        
        # Title
        if self.theme.title:
            ax.set_title(self.theme.title)
        
        # Aspect ratio
        ax.set_aspect(self.theme.aspect)
    
    def show(self) -> None:
        """Show the current plot."""
        self.apply_theme()
        plt.tight_layout()
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
        cmap: str | None = None,
        show_contours: bool = True,
        contour_levels: int = 10,
        show_colorbar: bool | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Add a horizon to the plot.
        
        Parameters
        ----------
        horizon : Horizon
            Horizon to visualize.
        x : np.ndarray
            1D array of x coordinates.
        y : np.ndarray
            1D array of y coordinates.
        cmap : str, optional
            Colormap name (default: uses theme cmap).
        show_contours : bool
            Whether to show contour lines (default: True).
        contour_levels : int
            Number of contour levels (default: 10).
        show_colorbar : bool, optional
            Whether to show colorbar (default: uses theme setting).
        **kwargs
            Additional kwargs passed to pcolormesh.
        
        Returns
        -------
        Self
            Returns self for method chaining.
        """
        if cmap is None:
            cmap = self.theme.cmap
        
        if show_colorbar is None:
            show_colorbar = self.theme.show_colorbar
        
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )

        _add_horizon(
            self.ax,
            horizon,
            x=x,
            y=y,
            cmap=cmap,
            show_contours=show_contours,
            contour_levels=contour_levels,
            show_colorbar=show_colorbar,
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

        show_top: bool = True,
        show_base: bool = True,
        show_thickness: bool = False,
        cmap: str | None = None,
        show_contours: bool = True,
        contour_levels: int = 10,
        show_colorbar: bool | None = None,
        **kwargs: Any,
    ) -> Self:
        """
        Add a zone to the plot.
        
        Parameters
        ----------
        zone : Zone
            Zone to visualize.
        x : np.ndarray
            1D array of x coordinates.
        y : np.ndarray
            1D array of y coordinates.
        show_top : bool
            Whether to show top surface (default: True).
        show_base : bool
            Whether to show base surface (default: True).
        show_thickness : bool
            Whether to show thickness map (default: False).
        cmap : str, optional
            Colormap name (default: uses theme cmap).
        show_contours : bool
            Whether to show contour lines (default: True).
        contour_levels : int
            Number of contour levels (default: 10).
        show_colorbar : bool, optional
            Whether to show colorbar (default: uses theme setting).
        **kwargs
            Additional kwargs passed to pcolormesh or contour.
        
        Returns
        -------
        Self
            Returns self for method chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )

        if show_colorbar is None:
            show_colorbar = self.theme.show_colorbar
        
        _add_zone(
            self.ax,
            zone,
            x=x,
            y=y,
            show_top=show_top,
            show_base=show_base,
            show_thickness=show_thickness,
            cmap=cmap,
            show_contours=show_contours,
            contour_levels=contour_levels,
            show_colorbar=show_colorbar,
            **kwargs,
        )
        
        return self
    
    def add_boundary_polygon(
        self,
        boundary: BoundaryPolygon,
        *,
        facecolor: str | tuple = 'lightblue',
        edgecolor: str | tuple = 'black',
        linewidth: float = 2.0,
        alpha: float = 0.3,
        show_fill: bool = True,
        show_vertices: bool = False,
        **kwargs: Any,
    ) -> Self:
        """
        Add a boundary polygon to the plot.
        
        Parameters
        ----------
        boundary : BoundaryPolygon
            Boundary polygon to visualize.
        facecolor : str or tuple
            Fill color for the polygon (default: 'lightblue').
        edgecolor : str or tuple
            Edge/border color (default: 'black').
        linewidth : float
            Width of the boundary line (default: 2.0).
        alpha : float
            Transparency of the fill (0-1, default: 0.3).
        show_fill : bool
            Whether to fill the polygon (default: True).
        show_vertices : bool
            Whether to show vertex markers (default: False).
        **kwargs
            Additional kwargs passed to matplotlib Polygon.
        
        Returns
        -------
        Self
            Returns self for method chaining.
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
            **kwargs,
        )
        
        return self
