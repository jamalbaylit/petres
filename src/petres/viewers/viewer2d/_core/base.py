from __future__ import annotations
from abc import ABC, abstractmethod


class Base2DViewer(ABC):
    """
    2D rendering engine interface. Viewer2D calls these methods; each backend implements them.
    Optional features should raise a consistent NotImplementedError via _unsupported().
    """

    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme) -> None:
        """Apply global scene settings (colors, axes, grid, etc.)."""

    @abstractmethod
    def show(self) -> None:
        """Show the current 2D plot."""

    # ---- optional features (default: not supported) ----
    def add_horizon(self, horizon, x, y, **kwargs) -> None:
        self._unsupported("add_horizon")

    def add_zone(self, zone, x, y, **kwargs) -> None:
        self._unsupported("add_zone")

    def add_boundary_polygon(self, boundary, **kwargs) -> None:
        self._unsupported("add_boundary_polygon")

    def add_wells(self, wells, **kwargs) -> None:
        self._unsupported("add_wells")

    def _unsupported(self, feature: str) -> None:
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
