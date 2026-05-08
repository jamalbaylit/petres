from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .._core.theme import Base3DViewerTheme

# CameraView = Literal[
#     "iso",      # 3D angled view
#     "top",      # map view
#     "bottom",
#     "front",    # look from +Y
#     "back",     # look from -Y
#     "right",    # look from +X
#     "left",     # look from -X
# ]

# @dataclass(frozen=True)
# class Camera3D:
#     """Define camera orientation controls for 3D scene rendering.

#     Parameters
#     ----------
#     view : {"iso", "top", "bottom", "front", "back", "right", "left"}, default="iso"
#         Base camera viewpoint preset.
#     tilt : float, default=0.0
#         Vertical tilt in degrees. Positive values reveal more top surface.
#     turn : float, default=0.0
#         Horizontal rotation in degrees around the vertical axis.
#     roll : float, default=0.0
#         Screen-space roll in degrees.
#     zoom : float, default=1.0
#         Zoom factor where ``1.0`` is neutral, values above ``1.0`` zoom in,
#         and values below ``1.0`` zoom out.
#     position : tuple[float, float, float], default=(0, 0, -1)
#         Absolute camera position in 3D space. Default looks towards the origin from the negative Z direction.
#     """

#     view: CameraView = "iso"

#     # “small intuitive knobs”
#     tilt: float = 0.0     # degrees: + = see more top, - = see more bottom
#     turn: float = 0.0     # degrees: rotate around vertical axis
#     roll: float = 0.0     # degrees: rotate the screen (usually keep 0)
#     zoom: float = 1.0     # 1.0 = normal, 1.2 = closer, 0.8 = farther
#     # focal_point = (0, 0, 0)
#     # up = (0, 1, 0)

Color = str | tuple[float, float, float] 

@dataclass(frozen=True)
class PyVista3DViewerTheme(Base3DViewerTheme):
    """Configure visual theme and camera settings for a 3D scene.

    Parameters
    ----------
    background : str | tuple[float, float, float], default="white"
        Scene background color.
    show_orientation_widget : bool, default=True
        Display the orientation widget in the viewer.
    show_coordinate_axes : bool, default=True
        Display coordinate axes in the scene.
    lighting : bool, default=True
        Enable lighting when adding shaded meshes to the scene.
    scale : tuple[float, float, float], default=(1.0, 1.0, 1.0)
        Per-axis scale multipliers for rendering.
    title_fontsize : int, default=12
        Font size for the scene title.
    title_color : str | tuple[float, float, float], default="black"
        Title text color.
    title_position : str, default="upper_edge"
        Viewer-specific anchor position for title placement.
    camera : Camera3D, default=Camera3D()
        Camera configuration applied to the scene.
    
    """

    background: Color = "white"
    show_orientation_widget: bool = True
    show_coordinate_axes: bool = True
    lighting: bool = True
    # show_grid: bool = True
    # camera_up: tuple[float, float, float] = (1, 1, -1)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
    direction: tuple[float, float, float] = (1, 1, -1)

    title_fontsize: int = 12
    title_color: Color = "black"
    title_position: str = "upper_edge"

    def __post_init__(self):
        self._validate_scale(self.scale)
        self._validate_direction(self.direction)

    @classmethod
    def _validate_scale(cls, scale):
        if not isinstance(scale, (tuple, list)):
            raise TypeError(
                "`scale` must be a tuple or list of 3 numeric values."
            )

        if len(scale) != 3:
            raise ValueError(
                "`scale` must contain exactly 3 values (x_scale, y_scale, z_scale)."
            )

        if not all(isinstance(v, (int, float)) for v in scale):
            raise TypeError(
                "All `scale` values must be numeric."
            )

        if any(v == 0 for v in scale):
            raise ValueError(
                "`scale` values cannot be zero."
            )
        
    @classmethod
    def _validate_direction(cls, direction):
        if not isinstance(direction, (tuple, list)):
            raise TypeError(
                "`direction` must be a tuple or list of 3 direction values."
            )

        if len(direction) != 3:
            raise ValueError(
                "`direction` must contain exactly 3 values (x_dir, y_dir, z_dir)."
            )

        if not all(isinstance(v, (int, float)) for v in direction):
            raise TypeError(
                "All `direction` values must be numeric."
            )

        if any(v != 1 and v != -1 for v in direction):
            raise ValueError(
                "`direction` values must be either 1 or -1."
            )
        






from typing import Tuple
import math
 
Vec3 = Tuple[float, float, float]
 
 
@dataclass(frozen=True)
class Camera3D:
    """Immutable camera configuration for a PyVista Plotter.
 
    Parameters
    ----------
    position : (x, y, z)
        Where the camera sits in world space.
    focal_point : (x, y, z)
        The point the camera looks at. Defaults to the origin.
    view_up : (x, y, z)
        Which direction is "up" for the camera. Defaults to +Z.
    zoom : float
        Zoom factor applied after positioning (1.0 = no zoom).
 
    Usage
    -----
        cam = Camera3D.isometric()
        cam.apply(plotter)
 
        # or inline:
        Camera3D(position=(5, 5, 5), focal_point=(0, 0, 0)).apply(plotter)
    """
 
    position:    Vec3  = (5.0,  5.0,  5.0)
    focal_point: Vec3  = (0.0,  0.0,  0.0)
    view_up:     Vec3  = (0.0,  0.0,  1.0)
    zoom:        float = 1.0
 
    # ------------------------------------------------------------------ #
    #  Core method                                                         #
    # ------------------------------------------------------------------ #
 
    def apply(self, plotter) -> None:
        """Push this camera configuration to a pyvista.Plotter instance."""
        plotter.camera_position = [
            self.position,
            self.focal_point,
            self.view_up,
        ]
        plotter.camera.zoom(self.zoom)
 
    # ------------------------------------------------------------------ #
    #  Derived helpers                                                     #
    # ------------------------------------------------------------------ #
 
    def with_zoom(self, zoom: float) -> "Camera3D":
        """Return a copy with a different zoom factor."""
        return Camera3D(self.position, self.focal_point, self.view_up, zoom)
 
    def looking_at(self, focal_point: Vec3) -> "Camera3D":
        """Return a copy aimed at a different focal point."""
        return Camera3D(self.position, focal_point, self.view_up, self.zoom)
 
    def translated(self, dx: float = 0, dy: float = 0, dz: float = 0) -> "Camera3D":
        """Shift camera position (and focal point) by a delta."""
        p = (self.position[0] + dx, self.position[1] + dy, self.position[2] + dz)
        f = (self.focal_point[0] + dx, self.focal_point[1] + dy, self.focal_point[2] + dz)
        return Camera3D(p, f, self.view_up, self.zoom)
 
    # ------------------------------------------------------------------ #
    #  Presets — call as Camera3D.front(), Camera3D.isometric(), …        #
    # ------------------------------------------------------------------ #
 
    @classmethod
    def front(cls, distance: float = 6.0) -> "Camera3D":
        """Straight-on front view (+Y axis)."""
        return cls(position=(0.0, -distance, 0.0),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def back(cls, distance: float = 6.0) -> "Camera3D":
        """Rear view (-Y axis)."""
        return cls(position=(0.0, distance, 0.0),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def left(cls, distance: float = 6.0) -> "Camera3D":
        """Left-side view (-X axis)."""
        return cls(position=(-distance, 0.0, 0.0),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def right(cls, distance: float = 6.0) -> "Camera3D":
        """Right-side view (+X axis)."""
        return cls(position=(distance, 0.0, 0.0),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def top(cls, distance: float = 6.0) -> "Camera3D":
        """Top-down plan view (+Z axis)."""
        return cls(position=(0.0, 0.0, distance),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 1.0, 0.0))
 
    @classmethod
    def bottom(cls, distance: float = 6.0) -> "Camera3D":
        """Bottom-up view (-Z axis)."""
        return cls(position=(0.0, 0.0, -distance),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 1.0, 0.0))
 
    @classmethod
    def isometric(cls, distance: float = 6.0) -> "Camera3D":
        """Classic +X +Y +Z isometric corner."""
        d = distance / math.sqrt(3)
        return cls(position=(d, d, d),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def isometric_sw(cls, distance: float = 6.0) -> "Camera3D":
        """-X -Y +Z corner (south-west)."""
        d = distance / math.sqrt(3)
        return cls(position=(-d, -d, d),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def isometric_se(cls, distance: float = 6.0) -> "Camera3D":
        """+X -Y +Z corner (south-east)."""
        d = distance / math.sqrt(3)
        return cls(position=(d, -d, d),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def isometric_nw(cls, distance: float = 6.0) -> "Camera3D":
        """-X +Y +Z corner (north-west)."""
        d = distance / math.sqrt(3)
        return cls(position=(-d, d, d),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))
 
    @classmethod
    def oblique(cls, azimuth: float = 45.0,
                elevation: float = 30.0,
                distance: float = 6.0) -> "Camera3D":
        """Arbitrary spherical position.
 
        Parameters
        ----------
        azimuth : degrees, 0 = +Y axis, CCW when viewed from above
        elevation : degrees above the XY plane
        distance : radius from the focal origin
        """
        az  = math.radians(azimuth)
        el  = math.radians(elevation)
        x = distance * math.cos(el) * math.sin(az)
        y = distance * math.cos(el) * math.cos(az)
        z = distance * math.sin(el)
        return cls(position=(x, y, z),
                   focal_point=(0.0, 0.0, 0.0),
                   view_up=(0.0, 0.0, 1.0))