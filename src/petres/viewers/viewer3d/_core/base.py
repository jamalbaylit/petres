from __future__ import annotations
from abc import ABC, abstractmethod
from .theme import Base3DViewerTheme
from ....grids.cornerpoint import CornerPointGrid
from ....grids.pillars import PillarGrid


class Base3DViewer(ABC):
    """
    Rendering engine interface. Viewer calls these methods; each backend implements them.
    Optional features should raise a consistent NotImplementedError via _unsupported().
    """

    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme: Base3DViewerTheme) -> None:
        """Apply global scene settings (background, axes, scale, camera convention)."""

    @abstractmethod
    def show(self) -> None:
        """Show the current 3D scene."""

    # ---- optional features (default: not supported) ----
    def reset_camera(self) -> None:
        self._unsupported("reset_camera")

    def add_corner_point_grid(self, grid: CornerPointGrid) -> None:
        self._unsupported("add_corner_point_grid")

    def add_pillars(self, pillars: PillarGrid) -> None:
        self._unsupported("add_pillars")

    # def add_wells(self, wells) -> None:
    #     self._unsupported("add_wells")

    # def add_zones(self, zones) -> None:
    #     self._unsupported("add_zones")

    def _unsupported(self, feature: str) -> None:
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
