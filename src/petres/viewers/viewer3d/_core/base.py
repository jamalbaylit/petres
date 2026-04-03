from __future__ import annotations
from abc import ABC, abstractmethod
from .theme import Base3DViewerTheme
from ....grids.cornerpoint import CornerPointGrid
from ....grids.pillars import PillarGrid


class Base3DViewer(ABC):
    """
    Define the interface for 3D viewer backends.

    Viewer layers call these methods while each rendering backend provides
    concrete implementations. Optional features are expected to raise a
    consistent ``NotImplementedError`` through ``_unsupported`` when not
    supported.
    """

    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme: Base3DViewerTheme) -> None:
        """Apply global scene settings.

        Parameters
        ----------
        theme : Base3DViewerTheme
            Scene-wide visual configuration including background, axes,
            scale, and camera convention.
        """

    @abstractmethod
    def show(self) -> None:
        """Render the current 3D scene."""

    # ---- optional features (default: not supported) ----
    def reset_camera(self) -> None:
        """Reset the active camera state.

        Raises
        ------
        NotImplementedError
            If the backend does not support camera reset.
        """
        self._unsupported("reset_camera")

    def add_corner_point_grid(self, grid: CornerPointGrid) -> None:
        """Add a corner-point grid to the scene.

        Parameters
        ----------
        grid : CornerPointGrid
            Grid object to render.

        Raises
        ------
        NotImplementedError
            If the backend does not support corner-point grids.
        """
        self._unsupported("add_corner_point_grid")

    def add_pillars(self, pillars: PillarGrid) -> None:
        self._unsupported("add_pillars")

    # def add_wells(self, wells) -> None:
    #     self._unsupported("add_wells")

    # def add_zones(self, zones) -> None:
    #     self._unsupported("add_zones")

    def _unsupported(self, feature: str) -> None:
        """Raise a standardized unsupported-feature error.

        Parameters
        ----------
        feature : str
            Name of the feature that is unavailable in the backend.

        Raises
        ------
        NotImplementedError
            Always raised to indicate a missing backend capability.
        """
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
