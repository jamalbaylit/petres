from dataclasses import dataclass, field
from typing import Optional, Mapping, Any

Color = str | tuple[float, float, float]  # keep it simple for users

@dataclass(frozen=True)
class SceneTheme3D:
    background: Color = "white"
    show_orientation_widget: bool = True
    show_coordinate_axes: bool = True
    # show_grid: bool = True
    camera_up: tuple[float, float, float] = (0, 0, -1)
    scale: tuple[float, float, float] = (1.0, 1.0, 1.0)
