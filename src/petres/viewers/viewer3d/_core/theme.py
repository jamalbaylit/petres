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
    """Immutable 3D camera configuration.

    Parameters
    ----------
    view : CameraView, optional
        Named preset orientation for the camera, by default ``"iso"``.
    tilt : float, optional
        Vertical tilt in degrees; positive tilts toward the top, negative
        toward the bottom, by default ``0.0``.
    turn : float, optional
        Rotation in degrees around the vertical axis, by default ``0.0``.
    roll : float, optional
        In-plane screen rotation in degrees; typically left at ``0.0``,
        by default ``0.0``.
    zoom : float, optional
        Zoom factor where ``1.0`` is normal, values greater than ``1.0`` zoom
        in, and values less than ``1.0`` zoom out, by default ``1.0``.
    depth_down : bool, optional
        When ``True`` the depth (Z) axis is displayed downward on screen,
        by default ``True``.
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
    """Immutable visual theme for a 3D scene.

    Parameters
    ----------
    background : Color, optional
        Background color of the scene, by default ``"white"``.
    show_orientation_widget : bool, optional
        Whether to display the orientation widget, by default ``True``.
    show_coordinate_axes : bool, optional
        Whether to display coordinate axes, by default ``True``.
    scale : tuple[float, float, float], optional
        Per-axis scale factors applied to the scene, by default
        ``(1.0, 1.0, 1.0)``.
    title_fontsize : int, optional
        Font size for the scene title in points, by default ``12``.
    title_color : Color, optional
        Color of the scene title text, by default ``"black"``.
    title_position : str, optional
        Anchor position of the scene title, by default ``"upper_edge"``.
    camera : Camera3D, optional
        Camera configuration, by default ``Camera3D()``.
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
