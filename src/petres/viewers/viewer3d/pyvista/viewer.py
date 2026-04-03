from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Self

<<<<<<< HEAD
from .layers.cornerpoint import _add_corner_point_grid
from .layers.pillars import _add_pillars
from .theme import PyVista3DViewerTheme, Camera3D
from ....grids.cornerpoint import CornerPointGrid
from ....grids.sampling._vertices import _resolve_xy_vertices
from .layers.surface import _add_surface
from petres.grids.pillars import PillarGrid
=======
import numpy as np
import pyvista as pv

from ...._utils._color import Color
from ....grids.cornerpoint import CornerPointGrid
from ....grids.sampling._vertices import _resolve_xy_vertices
>>>>>>> 6dd4196b505f52618203d97162d365d9377988f1
from ....models.horizon import Horizon
from .layers.zone import _add_zone
from ....models.zone import Zone
from .._core.base import Base3DViewer
from .._core.theme import Camera3D, SceneTheme3D
from .layers.cornerpoint import _add_corner_point_grid
from .layers.surface import _add_surface


class PyVista3DViewer(Base3DViewer):
    """Render and manage 3D geoscience scenes using PyVista.

    This viewer configures a PyVista plotter with a scene theme and camera,
    and provides helpers to add domain objects such as corner-point grids,
    zones, and horizons.

    Parameters
    ----------
    plotter : pyvista.Plotter or None, default=None
        Existing PyVista plotter to use. If ``None``, a new plotter is created.
    theme : SceneTheme3D or None, default=None
        Visual scene configuration. If ``None``, a default theme is used.
    camera : Camera3D or None, default=None
        Camera configuration. If ``None``, an isometric default camera setup
        is used.
    """

    theme: PyVista3DViewerTheme
    camera: Camera3D
    plotter: pv.Plotter

    def __init__(
        self, 
        plotter: pv.Plotter | None = None,
        theme: PyVista3DViewerTheme | None = None,
        camera: Camera3D | None = None,
    ) -> None:
        """Initialize viewer state with plotter, theme, and camera defaults.

        Raises
        ------
        AssertionError
            If resolved ``plotter``, ``theme``, or ``camera`` has an invalid type.
        """
        self.set_theme(theme or PyVista3DViewerTheme())
        self.set_camera(camera or Camera3D(
            view="iso",
            turn=-45,
            tilt=50,
            zoom=1.0,
            depth_down=True
        ))
        self.set_plotter(plotter or pv.Plotter())  

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
        p.set_background(theme.background, top=theme.background)
        p.show_axes() if theme.show_orientation_widget else p.hide_axes()
        p.show_bounds(
            grid='back',
            location='outer',
            all_edges=True,
        ) if theme.show_coordinate_axes else p.remove_bounds_axes()
        # p.set_scale(*theme.scale)
        # p.camera.up = theme.camera_up
        # p.show_grid() if theme.show_grid else p.remove_bounds_axes()

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
        self.apply_theme(self.theme)
        # self.plotter.set_viewup((-1, 0, 0))
        # self._set_y_front_slight_top(self.plotter, tilt=0.5)
        if title:
            self.plotter.add_text(
                str(title),
                position=self.theme.title_position,
                font_size=self.theme.title_fontsize,
                color=self.theme.title_color,
            )
        self.apply_camera(self.camera)
        self.plotter.show()
        self.plotter = pv.Plotter()
        
    def add_grid(
        self, 
        grid: CornerPointGrid, 
        *,
        show_inactive: bool = False,
        color: Any = None,
        scalars: np.ndarray | None = None,
        cmap: str | None = None,
        **kwargs: Any,
    ) -> Self:
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
        **kwargs : Any
            Additional keyword arguments forwarded to the grid layer renderer.

        Returns
        -------
        Self
            The current viewer instance for fluent chaining.

        Raises
        ------
        TypeError
            If ``grid`` is not a supported grid type.
        """

        match grid:
            case CornerPointGrid():
                self._add_corner_point_grid(grid, show_inactive=show_inactive, scalars=scalars, cmap=cmap, color=color,**kwargs)
            case _:
                raise TypeError(f"Unsupported grid type: {type(grid).__name__}")
        return self

    def add_pillars(
        self,
        pillars: PillarGrid,
        *,
        color: Any = "black",
        line_width: float = 2.5,
        **kwargs: Any,
    ) -> Self:
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
        Self
            The current viewer instance for fluent chaining.
        """
        _add_pillars(
            self.plotter,
            pillars.pillar_top,
            pillars.pillar_bottom,
            # color=color,
            # line_width=line_width,
            # **kwargs,
        )
        return self
    
    def apply_camera(self, cam: Camera3D) -> None:
        """Apply a camera preset and relative camera adjustments.

        Parameters
        ----------
        cam : Camera3D
            Camera configuration containing a view preset and optional turn,
            tilt, roll, zoom, and depth orientation adjustments.

        Raises
        ------
        ValueError
            If ``cam.view`` is not a recognized view preset.
        """
        p = self.plotter
        # Base view preset
        if cam.view == "iso":
            p.view_isometric()
        elif cam.view == "top":
            p.view_xy(negative=False)
        elif cam.view == "bottom":
            p.view_xy(negative=True)
        elif cam.view == "front":
            # front = "Y toward us" is easier with explicit camera, but keep preset for now
            p.view_yz(negative=False)
        elif cam.view == "back":
            p.view_yz(negative=True)
        elif cam.view == "right":
            p.view_xz(negative=False)
        elif cam.view == "left":
            p.view_xz(negative=True)
        else:
            raise ValueError(f"Unknown view: {cam.view}")

        # Depth down on screen (optional)
        if getattr(cam, "depth_down", False):
            p.camera.up = (0.0, 0.0, -1.0)

        # Apply intuitive tweaks as RELATIVE offsets
        if cam.turn:
            p.camera.azimuth = p.camera.azimuth + cam.turn
        if cam.tilt:
            p.camera.elevation = p.camera.elevation + cam.tilt
        if cam.roll:
            p.camera.roll = p.camera.roll + cam.roll

        if cam.zoom and cam.zoom != 1.0:
            p.camera.zoom(cam.zoom)

        p.reset_camera_clipping_range()


    def _add_corner_point_grid(
        self,
        grid: CornerPointGrid,
        show_inactive: bool = False,
        scalars: np.ndarray | None = None,
        cmap: str | None = None,
        color: Color | None = None,
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
        **kwargs : Any
            Extra keyword arguments forwarded to the layer renderer.
        """
        return _add_corner_point_grid(self, grid, show_inactive=show_inactive, scalars=scalars, cmap=cmap, color=color, **kwargs)


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
        cmap: str = "gist_rainbow",
        **kwargs: Any,
    ) -> Self:
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
        cmap : str, default="gist_rainbow"
            Colormap name used to assign a distinct color per zone.
        **kwargs : Any
            Additional keyword arguments forwarded to zone rendering.

        Returns
        -------
        Self
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
    ) -> Self:
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
        Self
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
        **kwargs: Any,
    ) -> Self:
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
        Self
            The current viewer instance for fluent chaining.
        """
        x, y = _resolve_xy_vertices(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            ni=ni, nj=nj,
            dx=dx, dy=dy,
        )
        depth = horizon.to_grid(x, y)  # shape: (ny, nx)
        _add_surface(self, depth, x=x, y=y, color=color, scalars=scalars, cmap=cmap, **kwargs)
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
        cmap: str = "turbo",
        **kwargs: Any,
    ) -> Self:
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
        cmap : str, default="turbo"
            Colormap name used to assign a distinct color per horizon.
        **kwargs : Any
            Additional keyword arguments forwarded to horizon rendering.

        Returns
        -------
        Self
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
            self.add_horizon(horizon, x=x, y=y, color=colors[i], **kwargs)
        return self



# from gridbuilder.model.data import WellInstance, ZoneInstance
# from matplotlib import pyplot as plt
# import pyvista as pv
# import numpy as np



# class Viewer3D:
#     plotter: pv.Plotter
#     xscale: float = 1.0
#     yscale: float = 1.0
#     zscale: float = 5.0

#     zone_line_width: float = 30
#     well_line_width: float = 10
#     well_line_color: str = "black"
#     wells_label_font_size: int = 15

#     def __init__(self, backend = PyVista3DBackend):
#         self.backend = backend()
    
#     def plot_wells(self, wells: list[WellInstance]):
#         average_length = np.mean([well.bottom - well.top for well in wells])
#         z_offset = average_length * 0.05
#         for well in wells:
#             point1 = (well.x, well.y, well.top)
#             point2 = (well.x, well.y, well.bottom)
#             poly = pv.Line(point1, point2)
#             # line = pv.Line(point1, point2)
#             # self.plotter.add_mesh(line, color=self.well_line_color, line_width=self.well_line_width)
#             mesh = poly.tube(
#                 radius=self.well_line_width,
#                 n_sides=16,
#                 capping=True
#             )
#             self.plotter.add_mesh(
#                 mesh,
#                 color=self.well_line_color,
#                 smooth_shading=True
#             )
            
#             # start_sphere = pv.Sphere(radius=0.2, center=point1)
#             # end_sphere = pv.Sphere(radius=0.2, center=point2)
#             # self.plotter.add_mesh(start_sphere, color='green')
#             # self.plotter.add_mesh(end_sphere, color='red')
#             label_position = (well.x, well.y, (well.top - z_offset)*self.zscale)  # Offset above top
#             self.plotter.add_point_labels(
#                 [label_position],
#                 [well.name],
#                 font_size=self.wells_label_font_size,
#                 text_color='white',
#                 bold=True,
#                 shadow=True,
#                 always_visible=True,
#                 show_points=False,     # explicitly disable point glyph
#                 shape_opacity=1,    # background box transparency
#             )

#     def plot_zones(self, zones: list[ZoneInstance]):
#         # 1. Zone Colors Setup
#         zone_names_unique = [zone.name for zone in zones]
#         cmap = plt.get_cmap("gist_rainbow")
#         colors = cmap(np.linspace(0, 1, len(zone_names_unique)))

#         # Dictionary mapping Zone Name -> RGB Tuple
#         zone_color_map = {
#             z: tuple(colors[i][:3])
#             for i, z in enumerate(zone_names_unique)
#         }

#         # 2. Prepare Data Arrays
#         x = []
#         y = []
#         top = []
#         bot = []
#         zone_names = []
#         label_points = []
#         label_texts = []

#         for zone in zones:
#             for layer in zone.layers:
#                 if layer.name == "R2-1a_Silt":
#                     print(f"Layer: {layer.name}, Zone: {zone.name}")
#                 for well, t, b in zip(layer.wells, layer.tops, layer.bottoms):
#                     x.append(well.x)
#                     y.append(well.y)
#                     top.append(t)
#                     bot.append(b)
#                     zone_names.append(zone.name)

#                     # ---- label at tube midpoint ----
#                     label_points.append([
#                         well.x * self.xscale,
#                         well.y * self.yscale,
#                         0.5 * (t + b)*self.zscale
#                     ])
#                     label_texts.append(layer.name)
#                     if layer.name=="R2-1a_Silt" and well.name=="TA-15":
#                         print("YEAAAAAh.....................")

#         # print(label_texts)
#         n = len(x)

#         # 3. Create Points
#         points = np.empty((2 * n, 3))
#         points[0::2] = np.column_stack((x, y, top))
#         points[1::2] = np.column_stack((x, y, bot))

#         # 4. Create Lines (VTK Format)
#         lines = np.column_stack([
#             np.full(n, 2),
#             np.arange(0, 2 * n, 2),
#             np.arange(1, 2 * n, 2)
#         ]).ravel()

#         poly = pv.PolyData(points, lines=lines)

#         # 5. Apply Colors (Cell Data)
#         poly.cell_data["zone_color"] = np.array(
#             [zone_color_map[z] for z in zone_names]
#         )

#         # 6. Create Tubes
#         mesh = poly.tube(
#             radius=self.zone_line_width,
#             n_sides=16,
#             capping=True
#         )

#         # 7. Add Mesh to Plotter
#         self.plotter.add_mesh(
#             mesh,
#             scalars="zone_color",
#             rgb=True,
#             smooth_shading=True
#         )
        
#         # 8. Add Labels for Layers        
#         self.plotter.add_point_labels(
#             np.array(label_points),
#             label_texts,
#             font_size=8,
#             text_color="black",
#             shape_opacity=0,    # background box transparency
#             shape_color="black",
#             bold=True,
#             shadow=False,
#             always_visible=False,
#             show_points=False,     # explicitly disable point glyph
#         )



        

#         # =====================================================
#         # NEW: Add Legend
#         # =====================================================
#         # Convert the map into a list of [label, color]
#         legend_entries = []
#         for zone_name, color in zone_color_map.items():
#             legend_entries.append([zone_name, color])

#         legend = self.plotter.add_legend(
#             labels=legend_entries,
#             loc='lower right',      # <--- Align to lower left corner

#             bcolor='black',        # Background color of the legend box
#             # border=True,           # Add a border around the legend
#             # size=[0.15, 0.15],     # Optional: Adjust scale of the legend box
#             face='circle'          # Icon shape
#         )
#         legend.SetBackgroundOpacity(0.2)
#         # Force layout calculation
#         # Get size in normalized viewport coordinates
#         legend.SetPadding(2)   # default is quite large
#         legend.SetPosition(0.91, 0.02)
        
#     def plot_layer_surface(
#         self,
#         x_coords: np.ndarray,
#         y_coords: np.ndarray,
#         z: np.ndarray,
#         layer_name: str,
#         cmap: str = "viridis",
#         opacity: float = 0.6,
#         show_edges: bool = False
#     ):
#         """
#         Plot a horizontal layer surface (top or bottom).
#         """

#         xx, yy = np.meshgrid(
#             x_coords,
#             y_coords,
#             indexing="ij"
#         )

#         zz = z

#         grid = pv.StructuredGrid(xx, yy, zz)

#         self.plotter.add_mesh(
#             grid,
#             cmap=cmap,
#             opacity=opacity,
#             show_edges=show_edges,
#             name=f"layer_{layer_name}"
#         )


#     def plot_layer_thickness(
#         self,
#         x_coords,
#         y_coords,
#         z_top,
#         z_bottom,
#         layer_name: str,
#         cmap: str = "plasma"
#     ):
#         thickness = z_bottom - z_top

#         xx, yy = np.meshgrid(
#             x_coords,
#             y_coords,
#             indexing="ij"
#         )

#         zz = z_top

#         grid = pv.StructuredGrid(xx, yy, zz)
#         grid["Thickness"] = thickness.ravel(order="F")

#         self.plotter.add_mesh(
#             grid,
#             scalars="Thickness",
#             cmap=cmap,
#             opacity=0.8,
#             scalar_bar_args={"title": f"{layer_name} Thickness"}
#         )

