from __future__ import annotations

from dataclasses import replace
from collections.abc import Sequence
from typing import Any
import pyvista as pv
import numpy as np

from ....models.wells import VerticalWell, _validate_well_sequence
from ....grids.sampling._vertices import _resolve_xy_vertices
from .layers.cornerpoint import _add_corner_point_grid
from .theme import PyVista3DViewerTheme, Camera3D
from ....grids.cornerpoint import CornerPointGrid
from ...._validation import _validate_z_scale
from ....config.colors import DEFAULT_CMAP
from ....grids.pillars import PillarGrid
from .layers.pillars import _add_pillars
from .layers.surface import _add_surface
from ....models.horizon import Horizon
from .._core.base import Base3DViewer
from .layers.wells import _add_well
from ...._utils._colors import Color
from .layers.zone import _add_zone
from ....models.zone import Zone

class PyVista3DViewer(Base3DViewer):
    """Render and manage 3D geoscience scenes using PyVista.

    This viewer configures a PyVista plotter with a scene theme and camera,
    and provides helpers to add domain objects such as corner-point grids,
    zones, and horizons.

    Parameters
    ----------
    plotter : pyvista.Plotter or None, default=None
        Existing PyVista plotter to use. If ``None``, a new plotter is created.
    theme : PyVista3DViewerTheme or None, default=None
        Visual scene configuration. If ``None``, a default theme is used.
    camera : Camera3D or None, default=None
        Camera configuration. If ``None``, an isometric default camera setup
        is used.
    title : str, default="Petres 3D Viewer"
        Optional title text shown in the viewer window.
    z_scale : float, default=1.0
        Scale factor for the z-axis to enhance vertical exaggeration.
    """

    theme: PyVista3DViewerTheme
    camera: Camera3D
    plotter: pv.Plotter
    _deferred_point_labels: list[tuple[np.ndarray, list[str], dict[str, Any]]]

    def __init__(
        self, 
        plotter: pv.Plotter | None = None,
        theme: PyVista3DViewerTheme | None = None,
        camera: Camera3D | None = None,
        title: str = "Petres 3D Viewer",
        z_scale: float | None = None,
    ) -> None:
        """Initialize viewer state with plotter, theme, and camera defaults.

        Raises
        ------
        AssertionError
            If resolved ``plotter``, ``theme``, or ``camera`` has an invalid type.
        """
        self.set_theme(theme or PyVista3DViewerTheme())
        self.set_camera(camera or Camera3D.isometric_se())
        self.set_plotter(plotter or pv.Plotter())
        self.title = title

        if z_scale is not None:
            self.set_z_scale(z_scale)

        self._deferred_point_labels = []

    def set_z_scale(self, z_scale: float) -> None:
        """Set the z-axis scale factor for vertical exaggeration.

        Parameters
        ----------
        z_scale : float
            Positive finite value used to scale the z-axis in the rendered scene.

        Raises
        ------
        ValueError
            If ``z_scale`` is not a positive finite float.
        """
        z_scale = _validate_z_scale(z_scale, name="z_scale")
        self.theme = replace(self.theme, scale=(self.theme.scale[0], self.theme.scale[1], z_scale))

    def set_plotter(self, plotter: pv.Plotter) -> None:
        """Assign the underlying PyVista plotter.

        Parameters
        ----------
        plotter : pyvista.Plotter
            Plotter instance used for all rendering operations.

        Raises
        ------
        AssertionError
            If ``plotter`` is not a ``pyvista.Plotter`` instance.
        """
        assert isinstance(plotter, pv.Plotter), "`plotter` must be a pyvista.Plotter instance."
        plotter.theme.allow_empty_mesh = self.theme.allow_empty_mesh
        self.plotter = plotter
        # Patch add_mesh to always disable lighting
        _original_add_mesh = plotter.add_mesh
        def _add_mesh_no_lighting(*args, **kwargs):
            kwargs.setdefault('lighting', self.theme.lighting)
            actor = _original_add_mesh(*args, **kwargs)
            # Apply global visual Z exaggeration
            scale = tuple(
                s * d for s, d in zip(self.theme.scale, self.theme.direction)
            )

            actor.SetScale(*scale)

            return actor
        plotter.add_mesh = _add_mesh_no_lighting

        self.plotter = plotter

    def set_theme(self, theme: PyVista3DViewerTheme) -> None:
        """Assign the active scene theme.

        Parameters
        ----------
        theme : PyVista3DViewerTheme
            Theme containing background, axes, and title display settings.

        Raises
        ------
        AssertionError
            If ``theme`` is not a ``PyVista3DViewerTheme`` instance.
        """
        assert isinstance(theme, PyVista3DViewerTheme), "`theme` must be a PyVista3DViewerTheme instance or None."
        self.theme = theme

    def set_camera(self, camera: Camera3D) -> None:
        """Assign the active camera configuration.

        Parameters
        ----------
        camera : Camera3D
            Camera preset and relative view adjustments used for rendering.

        Raises
        ------
        AssertionError
            If ``camera`` is not a ``Camera3D`` instance.
        """
        assert isinstance(camera, Camera3D), "`camera` must be a Camera3D instance or None."
        self.camera = camera

    def apply_theme(self, theme: PyVista3DViewerTheme) -> None:
        """Apply scene styling options to the active plotter.

        Parameters
        ----------
        theme : PyVista3DViewerTheme
            Theme values controlling background color and axes visibility.
        """

        p = self.plotter

        x_scale, y_scale, z_scale = theme.scale
        axes_ranges = [
            p.bounds[0] / x_scale,
            p.bounds[1] / x_scale,
            p.bounds[2] / y_scale,
            p.bounds[3] / y_scale,
            p.bounds[4] / z_scale,
            p.bounds[5] / z_scale,
        ]

        p.show_bounds(
            grid='back',
            location='outer',
            ticks='outside',
            minor_ticks=True,
            fmt="%.0f",
            use_2d=False,
            
            axes_ranges=axes_ranges,
            xtitle='X',
            ytitle='Y',
            ztitle='Z',
        )
        p.show_axes() if theme.show_orientation_widget else p.hide_axes()
        p.set_background(theme.background, top=theme.background)


    def _defer_point_labels(
        self,
        points: np.ndarray,
        labels: list[str],
        **kwargs: Any,
    ) -> None:
        self._deferred_point_labels.append((np.asarray(points, dtype=float), labels, kwargs))

    def _flush_deferred_point_labels(self) -> None:
        if not self._deferred_point_labels:
            return

        scale = np.asarray(self.theme.scale, dtype=float)
        direction = np.asarray(self.theme.direction, dtype=float)
        for points, labels, kwargs in self._deferred_point_labels:
            self.plotter.add_point_labels(points * scale * direction, labels, **kwargs)

        self._deferred_point_labels.clear()

    def reset_camera(self) -> None:
        """Reset camera position and clipping range to defaults."""
        self.plotter.reset_camera()
        self.plotter.reset_camera_clipping_range()

    def show(self, *, title: str | None = None) -> None:
        """Render the current scene and open the interactive viewer window.

        Parameters
        ----------
        title : str or None, default=None
            Optional scene title text displayed at the configured theme position.
        """

        # Always apply an explicit scale so repeated calls are deterministic.
        self._flush_deferred_point_labels()
        if title:
            self.plotter.add_text(
                str(title),
                position=self.theme.title_position,
                font_size=self.theme.title_fontsize,
                color=self.theme.title_color,
            )

            
        self.apply_theme(self.theme)
        self.apply_camera(self.camera)
        self.plotter.show(title=self.title)
        
        self.plotter.close()
        self.set_plotter(pv.Plotter())

        
    def add_grid(
        self, 
        grid: CornerPointGrid, 
        *,
        show_inactive: bool = False,
        color: Any = None,
        scalars: np.ndarray | None = None,
        cmap: str | None = None,
        colorbar_title: str | None = None,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add a supported grid to the current 3D scene.

        Parameters
        ----------
        grid : CornerPointGrid
            Grid object to visualize.
        show_inactive : bool, default=False
            If ``True``, include inactive cells in the rendered geometry.
        color : Any, default=None
            Optional fixed color override for the grid mesh.
        scalars : numpy.ndarray or None, default=None
            Optional scalar values for per-cell or per-point colormapping.
        cmap : str or None, default=None
            Matplotlib-compatible colormap name used when ``scalars`` is provided.
        colorbar_title : str or None, default=None
            Optional title for the scalar bar when ``scalars`` are provided.
        **kwargs : Any
            Additional keyword arguments forwarded to the grid layer renderer.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.

        Raises
        ------
        TypeError
            If ``grid`` is not a supported grid type.
        """

        if isinstance(grid, CornerPointGrid): 
            self._add_corner_point_grid(
                grid, 
                show_inactive=show_inactive, 
                scalars=scalars, 
                cmap=cmap, 
                color=color, 
                colorbar_title=colorbar_title, 
                **kwargs
            )
            return self
        
        raise TypeError(f"Unsupported grid type: {type(grid).__name__}")

    def add_pillars(
        self,
        pillars: PillarGrid,
        *,
        color: Any = "black",
        line_width: float = 2.5,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add a pillar grid to the current 3D scene.

        Parameters
        ----------
        pillars : PillarGrid
            Pillar grid model to render.
        color : Any, default="black"
            Color used for the pillar lines and direction arrows.
        line_width : float, default=2.5
            Width used when rendering the pillar line.
        **kwargs : Any
            Additional keyword arguments forwarded to the pillar layer renderer.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.
        """
        _add_pillars(
            self,
            pillars.pillar_top,
            pillars.pillar_bottom,
            color=color,
            line_width=line_width,
            **kwargs,
        )
        return self

    def add_wells(
        self,
        wells: Sequence[VerticalWell] | VerticalWell,
        *,
        label_font_size: float=15,
        label_color: Any='red',
        line_color: Any='red',
        line_width: float=2.0,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        
        wells = _validate_well_sequence(wells)
        line_color = Color(line_color).as_rgb() if line_color is not None else None
        label_color = Color(label_color).as_rgb() if label_color is not None else None

        for well in wells:
            _add_well(
                self,
                well_x=well.x,
                well_y=well.y,
                well_top=None,
                well_bottom=None,
                well_name=well.name,
                label_font_size=label_font_size,
                label_color=label_color,
                line_color=line_color,
                line_width=line_width,
                **kwargs,
            )
        return self
    
    # def apply_camera(self, cam: Camera3D) -> None:
    #     """Apply a camera preset and relative camera adjustments.

    #     Parameters
    #     ----------
    #     cam : Camera3D
    #         Camera configuration containing a view preset and optional turn,
    #         tilt, roll, zoom, and depth orientation adjustments.

    #     Raises
    #     ------
    #     ValueError
    #         If ``cam.view`` is not a recognized view preset.
    #     """
    #     p = self.plotter
    #     # Base view preset
    #     if cam.view == "iso":
    #         p.view_isometric()
    #     elif cam.view == "top":
    #         p.view_xy(negative=False)
    #     elif cam.view == "bottom":
    #         p.view_xy(negative=True)
    #     elif cam.view == "front":
    #         # front = "Y toward us" is easier with explicit camera, but keep preset for now
    #         p.view_yz(negative=False)
    #     elif cam.view == "back":
    #         p.view_yz(negative=True)
    #     elif cam.view == "right":
    #         p.view_xz(negative=False)
    #     elif cam.view == "left":
    #         p.view_xz(negative=True)
    #     else:
    #         raise ValueError(f"Unknown view: {cam.view}")

    #     # Depth down on screen (optional)
    #     # if getattr(cam, "depth_down", False):
    #     p.camera.position = cam.position
    #     # p.camera.focal_point = cam.focal_point
    #     # p.camera.up = cam.up

    #     # Apply intuitive tweaks as RELATIVE offsets
    #     if cam.turn:
    #         p.camera.azimuth = p.camera.azimuth + cam.turn
    #     if cam.tilt:
    #         p.camera.elevation = p.camera.elevation + cam.tilt
    #     if cam.roll:
    #         p.camera.roll = p.camera.roll + cam.roll

    #     if cam.zoom and cam.zoom != 1.0:
    #         p.camera.zoom(cam.zoom)

    #     self.reset_camera()


    # def apply_camera(self, cam: Camera3D) -> None:
    #     p = self.plotter

    #     # Reset once up front so the preset starts from a clean camera state.
    #     self.reset_camera()

    #     # 1. Apply base view preset
    #     if cam.view == "iso":
    #         p.view_isometric()
    #     elif cam.view == "top":
    #         p.view_xy(negative=False)
    #     elif cam.view == "bottom":
    #         p.view_xy(negative=True)
    #     elif cam.view == "front":
    #         # front = "Y toward us" is easier with explicit camera, but keep preset for now
    #         p.view_yz(negative=False)
    #     elif cam.view == "back":
    #         p.view_yz(negative=True)
    #     elif cam.view == "right":
    #         p.view_xz(negative=False)
    #     elif cam.view == "left":
    #         p.view_xz(negative=True)
    #     else:
    #         raise ValueError(f"Unknown view: {cam.view}")

    #     # 2. Apply the absolute camera placement before the relative tweaks.
    #     p.camera.position = (0, 0, 0)

    #     # 3. Apply relative tweaks after the base placement.
    #     p.camera.azimuth += cam.turn
    #     p.camera.elevation += cam.tilt
    #     p.camera.roll += cam.roll

    #     # 4. Reset clipping range only — keeps position, fixes near/far planes
    #     p.reset_camera_clipping_range()

    #     # 5. Apply zoom AFTER reset so it isn't overridden
    #     if cam.zoom and cam.zoom != 1.0:
    #         p.camera.zoom(cam.zoom)

    #     self.reset_camera()

    def apply_camera(self, cam: Camera3D) -> None:
        """Apply camera configuration to the active plotter.

        Parameters
        ----------
        cam : Camera3D
            Camera configuration with position, focal point, and view settings.
        """
        # Auto-fit camera to scene bounds first
        # self.plotter.view_isometric()
        self.reset_camera()
        cam.apply(self.plotter)
        self.reset_camera()
        


    def _add_corner_point_grid(
        self,
        grid: CornerPointGrid,
        show_inactive: bool = False,
        scalars: np.ndarray | None = None,
        cmap: str | None = None,
        color: Color | None = None,
        colorbar_title: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a corner-point grid layer.

        Parameters
        ----------
        grid : CornerPointGrid
            Corner-point grid model.
        show_inactive : bool, default=False
            Whether to display inactive cells.
        scalars : numpy.ndarray or None, default=None
            Scalar values used to color the mesh.
        cmap : str or None, default=None
            Colormap name for scalar coloring.
        color : Color or None, default=None
            Fixed color when scalar coloring is not used.
        colorbar_title : str or None, default=None
            Optional title for the scalar bar when ``scalars`` are provided.
        **kwargs : Any
            Extra keyword arguments forwarded to the layer renderer.
        """
        return _add_corner_point_grid(
            self, 
            grid, 
            show_inactive=show_inactive, 
            scalars=scalars, 
            cmap=cmap, 
            color=color, 
            colorbar_title=colorbar_title, 
            **kwargs
        )


    def add_zones(
        self,
        zones: Sequence[Zone],
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        show_layers: bool = True,
        cmap: str = DEFAULT_CMAP,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add multiple zones to the scene using a discrete colormap.

        Parameters
        ----------
        zones : Sequence[Zone]
            Zone models to render.
        x : numpy.ndarray or None, default=None
            X-vertex coordinates. If ``None``, computed from grid arguments.
        y : numpy.ndarray or None, default=None
            Y-vertex coordinates. If ``None``, computed from grid arguments.
        xlim : tuple[float, float] or None, default=None
            X-axis bounds used when generating vertices.
        ylim : tuple[float, float] or None, default=None
            Y-axis bounds used when generating vertices.
        ni : int or None, default=None
            Number of cells along X used for vertex generation.
        nj : int or None, default=None
            Number of cells along Y used for vertex generation.
        dx : float or None, default=None
            Cell size along X used for vertex generation.
        dy : float or None, default=None
            Cell size along Y used for vertex generation.
        show_layers : bool, default=True
            Whether to render individual layers within each zone.
        cmap : str, default=DEFAULT_CMAP
            Colormap name used to assign a distinct color per zone.
        **kwargs : Any
            Additional keyword arguments forwarded to zone rendering.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )
        colors = Color.get_discrete_cmap(len(zones), cmap=cmap)
        for i, zone in enumerate(zones):
            self.add_zone(zone, x=x, y=y, color=colors[i], show_layers=show_layers, **kwargs)
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
        color: Any | None = None,
        show_layers: bool = True,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add a single zone to the scene.

        Parameters
        ----------
        zone : Zone
            Zone model to render.
        x : numpy.ndarray or None, default=None
            X-vertex coordinates. If ``None``, computed from grid arguments.
        y : numpy.ndarray or None, default=None
            Y-vertex coordinates. If ``None``, computed from grid arguments.
        xlim : tuple[float, float] or None, default=None
            X-axis bounds used when generating vertices.
        ylim : tuple[float, float] or None, default=None
            Y-axis bounds used when generating vertices.
        ni : int or None, default=None
            Number of cells along X used for vertex generation.
        nj : int or None, default=None
            Number of cells along Y used for vertex generation.
        dx : float or None, default=None
            Cell size along X used for vertex generation.
        dy : float or None, default=None
            Cell size along Y used for vertex generation.
        color : Any or None, default=None
            Optional color override, converted to RGB when provided.
        show_layers : bool, default=True
            Whether to render individual zone layers.
        **kwargs : Any
            Additional keyword arguments forwarded to zone rendering.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )
        color = Color(color).as_rgb() if color is not None else None
        _add_zone(self, zone, x=x, y=y, color=color, show_layers=show_layers, **kwargs)
        return self
    

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
        color: Any | None = None,
        scalars: bool = True,
        cmap: str | None = None,
        colorbar_title: str | None = None,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add a single horizon surface to the scene.

        Parameters
        ----------
        horizon : Horizon
            Horizon model used to compute a depth surface.
        x : numpy.ndarray or None, default=None
            X-vertex coordinates. If ``None``, computed from grid arguments.
        y : numpy.ndarray or None, default=None
            Y-vertex coordinates. If ``None``, computed from grid arguments.
        xlim : tuple[float, float] or None, default=None
            X-axis bounds used when generating vertices.
        ylim : tuple[float, float] or None, default=None
            Y-axis bounds used when generating vertices.
        ni : int or None, default=None
            Number of cells along X used for vertex generation.
        nj : int or None, default=None
            Number of cells along Y used for vertex generation.
        dx : float or None, default=None
            Cell size along X used for vertex generation.
        dy : float or None, default=None
            Cell size along Y used for vertex generation.
        color : Any or None, default=None
            Optional fixed surface color.
        scalars : bool, default=True
            If ``True``, scalar-based coloring is enabled for the surface.
        cmap : str or None, default=None
            Colormap name used when scalar coloring is enabled.
        **kwargs : Any
            Additional keyword arguments forwarded to surface rendering.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )
        # add colorbar_title to kwargs if scalars is True and colorbar_title is provided
        
        depth = horizon.to_grid(x, y)  # shape: (ny, nx)
        _add_surface(
            self, 
            depth, 
            x=x, 
            y=y, 
            color=color, 
            scalars=scalars, 
            cmap=cmap, 
            colorbar_title=colorbar_title, 
            **kwargs
        )
        return self
        
    def add_horizons(
        self,
        horizons: Sequence[Horizon],
        *,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        cmap: str = DEFAULT_CMAP,
        scalars: bool = True,
        **kwargs: Any,
    ) -> PyVista3DViewer:
        """Add multiple horizons to the scene with distinct colors.

        Parameters
        ----------
        horizons : Sequence[Horizon]
            Horizon models to render.
        x : numpy.ndarray or None, default=None
            X-vertex coordinates. If ``None``, computed from grid arguments.
        y : numpy.ndarray or None, default=None
            Y-vertex coordinates. If ``None``, computed from grid arguments.
        xlim : tuple[float, float] or None, default=None
            X-axis bounds used when generating vertices.
        ylim : tuple[float, float] or None, default=None
            Y-axis bounds used when generating vertices.
        ni : int or None, default=None
            Number of cells along X used for vertex generation.
        nj : int or None, default=None
            Number of cells along Y used for vertex generation.
        dx : float or None, default=None
            Cell size along X used for vertex generation.
        dy : float or None, default=None
            Cell size along Y used for vertex generation.
        cmap : str, default=DEFAULT_CMAP
            Colormap name used to assign a distinct color per horizon.
        scalars : bool, default=True
            If ``True``, scalar-based coloring is enabled for the surface.
        **kwargs : Any
            Additional keyword arguments forwarded to horizon rendering.

        Returns
        -------
        PyVista3DViewer
            The current viewer instance for fluent chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )
        colors = Color.get_discrete_cmap(len(horizons), cmap=cmap)
        for i, horizon in enumerate(horizons):
            self.add_horizon(horizon, x=x, y=y, color=colors[i], scalars=scalars, **kwargs)
        return self


