from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from functools import wraps
from typing import Any
import pyvista as pv
import numpy as np

from ...._validation import _validate_z_scale, _validate_positive_int
from ....models.wells import VerticalWell, _validate_well_sequence
from ....grids.sampling._vertices import _resolve_xy_vertices
from .layers.cornerpoint import _add_corner_point_grid
from .theme import PyVista3DViewerTheme, Camera3D
from ....grids.cornerpoint import CornerPointGrid
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
    z_scale : float, default=1.0
        Scale factor for the z-axis to enhance vertical exaggeration.
    """

    theme: PyVista3DViewerTheme
    camera: Camera3D
    plotter: pv.Plotter
    
    _window_title = "Petres 3D Viewer"
    _scene_title: str | None = None
    _point_labels: list[tuple[Any, dict[str, Any]]]
    _meshes: list[tuple[Any, dict[str, Any]]]
    _lines: list[tuple[Any, dict[str, Any]]]
    _cached_camera: pv.Camera | None = None
    _cached_window_size: tuple[int, int] | None = None
    _pending_calls: list[tuple[Any, tuple[Any, ...], dict[str, Any]]]

    def __init__(
        self, 
        plotter: pv.Plotter | None = None,
        theme: PyVista3DViewerTheme | None = None,
        camera: Camera3D | None = None,
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
        self.set_plotter(plotter)

        if z_scale is not None:
            self.set_z_scale(z_scale)

        self._point_labels = []
        self._meshes = []
        self._lines = []
        self._pending_calls = []


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



    def set_plotter(self, plotter: pv.Plotter=None, record: bool = True) -> None:
        """Assign the underlying PyVista plotter.

        Parameters
        ----------
        plotter : pyvista.Plotter
            Plotter instance used for all rendering operations.
        record : bool, default=True
            Whether to record mesh additions for later replay.
                When enabled, all calls to ``plotter.add_mesh`` are recorded and can be replayed on a new plotter instance. This is useful when switching plotters or when the plotter needs to be reinitialized.
        Raises
        ------
        AssertionError
            If ``plotter`` is not a ``pyvista.Plotter`` instance.
        """
        if plotter is None:
            plotter = pv.Plotter()
            
        assert isinstance(plotter, pv.Plotter), "`plotter` must be a pyvista.Plotter instance."
        plotter =  self._override_plotter(plotter, record=record)
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

    def _apply_theme(self, theme: PyVista3DViewerTheme, plotter: pv.Plotter) -> pv.Plotter:
        """Apply scene styling options to the active plotter.

        Parameters
        ----------
        theme : PyVista3DViewerTheme
            Theme values controlling background color and axes visibility.
        plotter : pyvista.Plotter
            Plotter instance to which the theme is applied.
        """

        p = plotter

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
        if theme.background:
            p.set_background(theme.background, top=theme.background)
        return p

    # def _render_point_labels(self, plotter: pv.Plotter) -> pv.Plotter:
    #     if not self._point_labels:
    #         return plotter

    #     scale = np.asarray(self.theme.scale, dtype=float)
    #     direction = np.asarray(self.theme.direction, dtype=float)
    #     for args, kwargs in self._point_labels:
    #         print(len(self._point_labels))
    #         kwargs = kwargs.copy()
    #         use_kwargs = "points" in kwargs
    #         points = kwargs["points"] if use_kwargs else args[0]
    #         points = np.asarray(points, dtype=float).copy() * scale * direction
    #         if use_kwargs:
    #             kwargs["points"] = points
    #         else:
    #             args = (points, *args[1:])
            
    #         plotter.add_point_labels(*args, **kwargs)

    #       self._point_labels.clear()
    #       return plotter

    def _reset_camera(self, plotter: pv.Plotter) -> pv.Plotter:
        """Reset camera position and clipping range to defaults."""
        plotter.reset_camera()
        plotter.reset_camera_clipping_range()
        return plotter

    def _override_plotter(self, plotter: pv.Plotter, record: bool = True) -> pv.Plotter:
        """Override the PyVista plotter.

        Parameters
        ----------
        plotter : pyvista.Plotter
            Plotter instance used for all rendering operations.
        record : bool, default=True
            Whether to record mesh additions for later replay.
                When enabled, all calls to ``plotter.add_mesh`` are recorded and can be replayed on a new plotter instance. This is useful when switching plotters or when the plotter needs to be reinitialized.
        Returns
        -------
        pyvista.Plotter
            The provided plotter instance with overridden ``add_mesh`` method to apply theme scaling and optional recording.
                            
        Raises
        ------
        AssertionError
            If ``plotter`` is not a ``pyvista.Plotter`` instance.
        """
        assert isinstance(plotter, pv.Plotter), "`plotter` must be a pyvista.Plotter instance."
        plotter.theme.allow_empty_mesh = self.theme.allow_empty_mesh
        self.plotter = plotter

        # Override add_mesh to apply theme scaling and direction to all added meshes
        _original_add_mesh = plotter.add_mesh
        def _add_mesh(*args, **kwargs):
            kwargs.setdefault('lighting', self.theme.lighting)
            actor = _original_add_mesh(*args, **kwargs)
            scale = tuple(
                s * d for s, d in zip(self.theme.scale, self.theme.direction)
            )

            actor.SetScale(*scale)

            if record: 
                self._meshes.append((args, kwargs.copy()))
            return actor
        plotter.add_mesh = _add_mesh
        
        _original_add_point_labels = plotter.add_point_labels
    
        def _add_point_labels(*args, **kwargs):
            if record:
                self._point_labels.append((args, kwargs.copy()))
            scaling = kwargs.pop("scaling", True)
            if scaling:
                scale = np.asarray(self.theme.scale, dtype=float)
                direction = np.asarray(self.theme.direction, dtype=float)

                kwargs = kwargs.copy()
                use_kwargs = "points" in kwargs
                points = kwargs["points"] if use_kwargs else args[0]
                
                if record:
                    self._point_labels.append((args, kwargs.copy()))
                points = np.asarray(points, dtype=float).copy()
                points *= scale * direction

                
                if use_kwargs:
                    kwargs["points"] = points
                else:
                    args = (points, *args[1:])
            return _original_add_point_labels(*args, **kwargs)
        plotter.add_point_labels = _add_point_labels

        _original_add_lines = plotter.add_lines
        def _add_lines(*args, **kwargs):
            if record:
                self._lines.append((args, kwargs.copy()))
            return _original_add_lines(*args, **kwargs)
        plotter.add_lines = _add_lines
        
        if record: 
            # _original_close = plotter.close
            # def _close(*args, **kwargs):
            #     if plotter.camera is not None:
            #         self._cached_camera = plotter.camera.copy()

            #     if plotter.render_window is not None:
            #         print("Updating cached window size for screenshot...")
            #         self._cached_window_size = tuple(
            #             plotter.render_window.GetSize()
            #         )
            #         print(f"Cached window size: {self._cached_window_size}")
            #     return _original_close(*args, **kwargs)
            # plotter.close = _close

            
            def _on_window_close(obj, event):
                if plotter.render_window is not None:
                    self._cached_window_size = tuple(plotter.render_window.GetSize())
                if plotter.camera is not None:
                    self._cached_camera = plotter.camera.copy()

            plotter.iren.interactor.AddObserver("ExitEvent", _on_window_close)


        return plotter

    def _render_queued(self) -> pv.Plotter:
        for func, args, kwargs in self._pending_calls:
            func(self, *args, **kwargs)
        self._pending_calls.clear()

    def _render(self, plotter: pv.Plotter, title: str | None = None) -> pv.Plotter:
        # plotter = self._render_point_labels(plotter)
        self._render_queued()
        plotter = self._apply_theme(self.theme, plotter)
        if title:
            plotter.add_text(
                str(title),
                position=self.theme.title_position,
                font_size=self.theme.title_fontsize,
                color=self.theme.title_color,
            )
        return plotter


    def show(
        self, 
        *, 
        title: str | None = None,
    ) -> None:
        """Render the current scene and open the interactive viewer window.

        Parameters
        ----------
        title : str or None, default=None
            Optional scene title text displayed at the configured theme position.
        """
        self.plotter=self._render(self.plotter, title=title)
        self.plotter = self._apply_camera(self.camera, self.plotter)
        self.plotter.show(title=self._window_title)
        self.plotter.close()
        self.set_plotter()
        


    def screenshot(
        self,
        path: str,
        *,
        transparent: bool = False,
        width: int = None,
        height: int = None,
    ) -> None:
        """
            Save a screenshot of the current plotter window to an image file.

            Parameters
            ----------
            path : str
                File path where the screenshot image will be saved.
            transparent : bool, default=False
                Whether the background should be transparent. If ``True``, the background color is ignored and the output image will have an alpha channel with transparency.
            width : int
                Desired output image width in pixels.
            height : int
                Desired output image height in pixels.

            Returns
            -------
            None
                This method saves the screenshot to disk and does not return anything.

            Notes
            -----
            This method can be called directly after ``show()``. In that case it
            reuses the cached scene camera and window size captured when the
            viewer was closed. If ``width`` and ``height`` are not provided, the
            last known window size is used. The viewer is rendered off-screen and
            the result is saved directly to ``path`` using the requested pixel
            dimensions.
        """



        window_size = None
        if self._cached_window_size is not None:
            window_size = self._cached_window_size
        
        if width is not None and height is not None:
            width = _validate_positive_int(width, name="width")
            height = _validate_positive_int(height, name="height")
            window_size = (width, height)

        plotter = pv.Plotter(off_screen=True)
        plotter = self._override_plotter(plotter, record=False)
        # plotter = self._render(plotter, title=self._scene_title)

        for args, kwargs in self._meshes:
            plotter.add_mesh(*args, **kwargs)

        for args, kwargs in self._point_labels:
            plotter.add_point_labels(*args, **kwargs)

        for args, kwargs in self._lines:
            plotter.add_lines(*args, **kwargs)


        if self._cached_camera is not None:
            plotter.camera = self._cached_camera 
        else:
            plotter = self._apply_camera(self.camera, plotter)

        plotter = self._render(plotter, title=self._scene_title)
        if transparent:
            plotter.background_color = (1,1,1,0)

        screenshot_kwargs = {"window_size": window_size}
        if transparent:
            screenshot_kwargs["transparent_background"] = True

        try:
            plotter.screenshot(path, **screenshot_kwargs)
        except TypeError:
            screenshot_kwargs.pop("transparent_background", None)
            plotter.screenshot(path, **screenshot_kwargs)

    @staticmethod
    def _queued(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, "_pending_calls"):
                self._pending_calls = []

            self._pending_calls.append((func, args, kwargs))
        return wrapper
        
    def add_grid(
        self, 
        grid: CornerPointGrid, 
        *,
        show_inactive: bool = False,
        color: Any = None,
        scalars: str | None = None,
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
        scalars : str or None, optional
            Property name to color by; if ``None`` uses solid color.
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
            scalars_arr = grid._resolve_source(scalars) if scalars is not None else None
            colorbar_title = str(scalars).strip().capitalize() if scalars_arr is not None else None
 
            self._add_corner_point_grid(
                grid, 
                show_inactive=show_inactive, 
                scalars=scalars_arr, 
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
            self.plotter,
            pillars.pillar_top,
            pillars.pillar_bottom,
            color=color,
            line_width=line_width,
            **kwargs,
        )
        return self

    @_queued
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

        bounds = self.plotter.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
        z_min, z_max = bounds[4], bounds[5]
        # Add a small margin so the tube visually extends beyond the data
        margin = abs(z_max - z_min) * 0.05 if z_max != z_min else 1.0
        top = z_max + margin
        bottom = z_min - margin

        for well in wells:
            _add_well(
                self.plotter,
                well_x=well.x,
                well_y=well.y,
                well_top=top,
                well_bottom=bottom,
                well_name=well.name,
                label_font_size=label_font_size,
                label_color=label_color,
                line_color=line_color,
                line_width=line_width,
                **kwargs,
            )
        return self

    def _apply_camera(self, cam: Camera3D, plotter: pv.Plotter) -> pv.Plotter:
        """Apply camera configuration to the active plotter.

        Parameters
        ----------
        cam : Camera3D
            Camera configuration with position, focal point, and view settings.
        plotter : pyvista.Plotter
            Plotter instance to which the camera configuration is applied.
        """
        # Auto-fit camera to scene bounds first
        # self.plotter.view_isometric()
        self._reset_camera(plotter)
        cam.apply(plotter)
        self._reset_camera(plotter)
        return plotter

        


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
            self.plotter, 
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


