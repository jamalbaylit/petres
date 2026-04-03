from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class Base2DViewer(ABC):
    """
    Define the backend interface for 2D rendering.

    Viewer2D calls these methods, and each concrete backend is expected to
    implement the required operations. Optional features should raise a
    consistent ``NotImplementedError`` via ``_unsupported``.
    """

    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme: Any) -> None:
        """
        Apply global scene settings.

        Parameters
        ----------
        theme : Any
            Theme definition used by the concrete backend.
        """

    @abstractmethod
    def show(self) -> None:
        """
        Render the current 2D scene.
        """

    # ---- optional features (default: not supported) ----
    def add_horizon(self, horizon: Any, x: Any, y: Any, **kwargs: Any) -> None:
        """
        Add a horizon to the scene.

        Parameters
        ----------
        horizon : Any
            Horizon object to render.
        x : Any
            X coordinates or axis values.
        y : Any
            Y coordinates or axis values.
        **kwargs : Any
            Backend-specific rendering options.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        self._unsupported("add_horizon")

    def add_zone(self, zone: Any, x: Any, y: Any, **kwargs: Any) -> None:
        """
        Add a zone to the scene.

        Parameters
        ----------
        zone : Any
            Zone object to render.
        x : Any
            X coordinates or axis values.
        y : Any
            Y coordinates or axis values.
        **kwargs : Any
            Backend-specific rendering options.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        self._unsupported("add_zone")

    def add_boundary_polygon(self, boundary: Any, **kwargs: Any) -> None:
        """
        Add a boundary polygon to the scene.

        Parameters
        ----------
        boundary : Any
            Boundary geometry to render.
        **kwargs : Any
            Backend-specific rendering options.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        self._unsupported("add_boundary_polygon")

    def add_wells(self, wells: Any, **kwargs: Any) -> None:
        """
        Add wells to the scene.

        Parameters
        ----------
        wells : Any
            Well collection to render.
        **kwargs : Any
            Backend-specific rendering options.

        Raises
        ------
        NotImplementedError
            Always raised by the base implementation.
        """
        self._unsupported("add_wells")

    def _unsupported(self, feature: str) -> None:
        """
        Raise a consistent error for an unsupported feature.

        Parameters
        ----------
        feature : str
            Feature name reported in the exception message.

        Raises
        ------
        NotImplementedError
            Always raised to indicate missing backend support.
        """
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
