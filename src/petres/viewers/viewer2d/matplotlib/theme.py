from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Color = str | tuple[float, float, float] | tuple[float, float, float, float]


@dataclass(frozen=True)
class Matplotlib2DViewerTheme:
    """General theme settings for 2D Matplotlib viewers."""

    # Figure
    figure_size: tuple[float, float] = (9.0, 7.0)
    dpi: int = 120
    constrained_layout: bool = True

    # Axes
    background: Color = "white"
    aspect: Literal["auto", "equal"] = "equal"
    margins: float = 0.03

    # Grid
    grid: bool = True
    grid_alpha: float = 0.18
    grid_linestyle: str = "--"
    grid_linewidth: float = 0.6

    # Labels
    xlabel: str = "X Axis"
    ylabel: str = "Y Axis"
    show_labels: bool = True

    # Title
    title_fontsize: float = 13.0

    # Spines / ticks
    hide_top_right_spines: bool = True
    tick_labelsize: float = 10.0