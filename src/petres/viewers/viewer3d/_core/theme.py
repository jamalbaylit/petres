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
    """Immutable 3-D camera configuration.

    Parameters
    ----------
    view : CameraView, optional
        Named preset direction from which the scene is observed.
        Defaults to ``"iso"`` (diagonal isometric view).
    tilt : float, optional
        Vertical offset in degrees.  Positive values reveal more of the
        top surface; negative values reveal more of the bottom.
        Defaults to ``0.0``.
    turn : float, optional
        Rotation around the vertical axis in degrees.  Defaults to ``0.0``.
    roll : float, optional
        Screen-plane rotation in degrees.  Keep at ``0.0`` for an upright
        horizon.  Defaults to ``0.0``.
    zoom : float, optional
        Magnification factor where ``1.0`` is the default field of view,
        values above ``1.0`` zoom in, and values below ``1.0`` zoom out.
        Defaults to ``1.0``.
    depth_down : bool, optional
        When ``True`` the depth (Z) axis is oriented visually downward on
        the screen.  Defaults to ``True``.
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
    """Immutable visual theme for a 3-D scene.

    Parameters
    ----------
    background : Color, optional
        Background color expressed as a CSS name string or an RGB
        triple of floats in ``[0, 1]``.  Defaults to ``"white"``.
    show_orientation_widget : bool, optional
        Display the orientation cube / compass widget.  Defaults to ``True``.
    show_coordinate_axes : bool, optional
        Overlay the XYZ axis triad.  Defaults to ``True``.
    scale : tuple[float, float, float], optional
        Multiplicative scale factors applied to the X, Y, and Z axes
        respectively.  Defaults to ``(1.0, 1.0, 1.0)``.
    title_fontsize : int, optional
        Font size (in points) for the scene title.  Defaults to ``12``.
    title_color : Color, optional
        Color of the scene title text.  Defaults to ``"black"``.
    title_position : str, optional
        Anchor position for the title label (e.g. ``"upper_edge"``).
        Defaults to ``"upper_edge"``.
    camera : Camera3D, optional
        Camera configuration applied to the scene.
        Defaults to :class:`Camera3D` with all defaults.
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
