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
    background: Color = "white"
    show_orientation_widget: bool = True
    show_coordinate_axes: bool = True
    # show_grid: bool = True
    # camera_up: tuple[float, float, float] = (1, 1, -1)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)

    camera: Camera3D = Camera3D()
