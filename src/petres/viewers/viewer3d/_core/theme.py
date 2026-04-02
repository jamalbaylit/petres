from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

CameraView = Literal[
    "iso",      # 3D angled view
    "top",      # map view
    "bottom",
    "front",    # look from +Y
    "back",     # look from -Y
    "right",    # look from +X
    "left",     # look from -X
]

@dataclass(frozen=True)
class Camera3D:
    """Define camera orientation controls for 3D scene rendering.

    Parameters
    ----------
    view : {"iso", "top", "bottom", "front", "back", "right", "left"}, default="iso"
        Base camera viewpoint preset.
    tilt : float, default=0.0
        Vertical tilt in degrees. Positive values reveal more top surface.
    turn : float, default=0.0
        Horizontal rotation in degrees around the vertical axis.
    roll : float, default=0.0
        Screen-space roll in degrees.
    zoom : float, default=1.0
        Zoom factor where ``1.0`` is neutral, values above ``1.0`` zoom in,
        and values below ``1.0`` zoom out.
    depth_down : bool, default=True
        Keep depth (Z) visually oriented downward on screen.
    """

    view: CameraView = "iso"

    # “small intuitive knobs”
    tilt: float = 0.0     # degrees: + = see more top, - = see more bottom
    turn: float = 0.0     # degrees: rotate around vertical axis
    roll: float = 0.0     # degrees: rotate the screen (usually keep 0)
    zoom: float = 1.0     # 1.0 = normal, 1.2 = closer, 0.8 = farther

    # optional: keep depth (Z) visually downward on screen
    depth_down: bool = True

Color = str | tuple[float, float, float] 
@dataclass(frozen=True)

class SceneTheme3D:
    """Configure visual theme and camera settings for a 3D scene.

    Parameters
    ----------
    background : str | tuple[float, float, float], default="white"
        Scene background color.
    show_orientation_widget : bool, default=True
        Display the orientation widget in the viewer.
    show_coordinate_axes : bool, default=True
        Display coordinate axes in the scene.
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
    # show_grid: bool = True
    # camera_up: tuple[float, float, float] = (1, 1, -1)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)

    title_fontsize: int = 12
    title_color: Color = "black"
    title_position: str = "upper_edge"

    camera: Camera3D = Camera3D()
