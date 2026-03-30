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


class Matplotlib2DViewer(Base2DViewer):
    def __init__(self, fig=None, ax=None, theme=None) -> None:
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
        self.theme = theme

    def apply_theme(self) -> None:
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
        """Add a horizon to the plot."""
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
        """Add a zone to the plot."""
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
        facecolor: str | tuple = "#7ec8e3",
        edgecolor: str | tuple = "#1f2937",
        linewidth: float = 1.8,
        alpha: float = 0.30,
        show_fill: bool = True,
        show_vertices: bool = False,
        vertex_color: str | tuple | None = None,
        vertex_size: float = 24.0,
        show_label: bool = True,
        label: str | None = None,
        label_fontsize: float = 10.0,
        label_box: bool = True,
        pad_ratio: float | None = None,
        **kwargs: Any,
    ) -> Self:
        """Add a boundary polygon to the plot."""
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