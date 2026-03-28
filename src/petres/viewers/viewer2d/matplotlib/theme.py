from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Color = str | tuple[float, float, float]

@dataclass(frozen=True)
class Matplotlib2DViewerTheme:
    """Theme settings for 2D matplotlib plots."""
    
    # Figure settings
    figure_size: tuple[float, float] = (10, 8)
    dpi: int = 100
    
    # Axes settings
    background: Color = "white"
    grid: bool = True
    grid_alpha: float = 0.3
    
    # Axis labels
    xlabel: str = "X"
    ylabel: str = "Y"
    show_labels: bool = True
    
    # Title
    title: str | None = None
    
    # Colorbar
    show_colorbar: bool = True
    cmap: str = "viridis"
    
    # Aspect ratio
    aspect: Literal["auto", "equal"] = "equal"
