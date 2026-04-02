from __future__ import annotations
from abc import ABC, abstractmethod
from .._core.theme import SceneTheme3D
from ....grids.cornerpoint import CornerPointGrid


class Base3DViewer(ABC):
    """
    Rendering engine interface for 3D viewers.

    Viewer calls these methods; each backend implements them.
    Optional features should raise a consistent NotImplementedError via _unsupported().
    """


    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme: SceneTheme3D) -> None:
        """Apply global scene settings (background, axes, scale, camera convention).

        Parameters
        ----------
        theme : SceneTheme3D
            The scene theme containing global rendering settings to apply.
        """

    @abstractmethod
    def show(self) -> None:
        """Show the current 3D scene."""

    # ---- optional features (default: not supported) ----
    def reset_camera(self) -> None:
        """Reset the camera to its default position.

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
            The corner-point grid to render.

        Raises
        ------
        NotImplementedError
            If the backend does not support corner-point grids.
        """
        self._unsupported("add_corner_point_grid")

    # def add_wells(self, wells) -> None:
    #     self._unsupported("add_wells")

    # def add_zones(self, zones) -> None:
    #     self._unsupported("add_zones")

    def _unsupported(self, feature: str) -> None:
        """Raise NotImplementedError for unsupported backend features.

        Parameters
        ----------
        feature : str
            Name of the unsupported feature.

        Raises
        ------
        NotImplementedError
            Always raised to signal that the feature is not supported by this backend.
        """
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
