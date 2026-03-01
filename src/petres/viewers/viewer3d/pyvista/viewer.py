# backend.py
from __future__ import annotations

from typing import Any, Self
import pyvista as pv
import numpy as np

from .layers.corner_point_grid import _add_corner_point_grid
from ....grids.cornerpoint import CornerPointGrid
from ...._utils._grid import _resolve_xy_sampling
from .layers.horizon import _add_horizon
from ....grids.pillar import PillarGrid
from .._core.theme import SceneTheme3D
from ....model.horizon import Horizon
from .._core.base import Base3DViewer
from ...._utils._color import Color
from .layers.zone import _add_zone
from ....model.zone import Zone


class PyVista3DViewer(Base3DViewer):
    def __init__(
        self, 
        plotter: pv.Plotter | None = None,
        theme: SceneTheme3D | None = None,
    ):
        self.plotter = plotter or pv.Plotter()
        self._theme = theme or SceneTheme3D()

    def set_theme(self, theme: SceneTheme3D) -> None:
        self._theme = theme

    def apply_theme(self, theme: SceneTheme3D):
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

    def reset_camera(self):
        self.plotter.reset_camera()
        self.plotter.reset_camera_clipping_range()

    def show(self):
        self.apply_theme(self._theme)
        self.plotter.show()
        
    def add_grid(self, grid: CornerPointGrid, **kwargs) -> Self:
        """Add a grid to the current 3D scene (rectilinear, corner-point, etc.)."""

        match grid:
            case CornerPointGrid():
                self._add_corner_point_grid(grid, **kwargs)
            case _:
                raise TypeError(f"Unsupported grid type: {type(grid).__name__}")
        return self
    
    def _add_corner_point_grid(self, grid, **kwargs) -> None:
        return _add_corner_point_grid(self, grid, **kwargs)

    def add_zone(
            self,
            zone: Zone,
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
            show_layers: bool = True,
            **kwargs,
        ) -> Self:
            x, y = _resolve_xy_sampling(
                x=x, y=y,
                xlim=xlim, ylim=ylim,
                nx=nx, ny=ny,
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
        nx: int | None = None,
        ny: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        color: Any | None = None,
        **kwargs,
    ) -> Self:
        x, y = _resolve_xy_sampling(
            x=x, y=y,
            xlim=xlim, ylim=ylim,
            nx=nx, ny=ny,
            dx=dx, dy=dy,
        )
        _add_horizon(self, horizon, x=x, y=y, color=color, **kwargs)
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

#     def show(self):
#         p = self.plotter
#         p.reset_camera_clipping_range()
#         p.set_background("#e6e6e6", top="#bdbdbd")
#         p.set_scale(xscale=self.xscale, yscale=self.yscale, zscale=self.zscale)
#         p.show_axes()
#         p.show_grid()
#         # p.camera_position = "xy"   # or "iso"
#         p.camera.up = (0, 0, -1)
#         p.show()
#         # print(self.plotter.bounds)


