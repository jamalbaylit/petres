from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

import numpy as np

from ....models.boundary import BoundaryPolygon
from ....models.horizon import Horizon
from ....models.wells import VerticalWell
from ....models.zone import Zone


class Base2DViewer(ABC):
    """2D rendering engine interface.

    Viewer2D calls these methods; each backend implements them.
    Optional features should raise a consistent ``NotImplementedError``
    via :meth:`_unsupported`.
    """

    # ---- core (must exist for any backend) ----
    @abstractmethod
    def set_theme(self, theme: Any) -> None:
        """Apply global scene settings (colors, axes, grid, etc.)."""

    @abstractmethod
    def show(self) -> None:
        """Show the current 2D plot."""

    # ---- optional features (default: not supported) ----
    def add_horizon(
        self,
        horizon: Horizon,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a horizon scalar map to the 2D axes.

        Parameters
        ----------
        horizon : Horizon
            Horizon instance to render.
        x : ndarray or None, default=None
            1D array of x-vertex coordinates. Must be provided with ``y``.
        y : ndarray or None, default=None
            1D array of y-vertex coordinates. Must be provided with ``x``.
        **kwargs : Any
            Additional keyword arguments forwarded to the backend renderer.

        Raises
        ------
        NotImplementedError
            If the backend does not support this feature.
        """
        self._unsupported("add_horizon")

    def add_zone(
        self,
        zone: Zone,
        x: np.ndarray | None = None,
        y: np.ndarray | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a zone scalar map to the 2D axes.

        Parameters
        ----------
        zone : Zone
            Zone instance to render.
        x : ndarray or None, default=None
            1D array of x-vertex coordinates. Must be provided with ``y``.
        y : ndarray or None, default=None
            1D array of y-vertex coordinates. Must be provided with ``x``.
        **kwargs : Any
            Additional keyword arguments forwarded to the backend renderer.

        Raises
        ------
        NotImplementedError
            If the backend does not support this feature.
        """
        self._unsupported("add_zone")

    def add_boundary_polygon(
        self,
        boundary: BoundaryPolygon,
        **kwargs: Any,
    ) -> None:
        """Add a boundary polygon overlay to the 2D axes.

        Parameters
        ----------
        boundary : BoundaryPolygon
            Boundary polygon instance to render.
        **kwargs : Any
            Additional keyword arguments forwarded to the backend renderer.

        Raises
        ------
        NotImplementedError
            If the backend does not support this feature.
        """
        self._unsupported("add_boundary_polygon")

    def add_wells(
        self,
        wells: Sequence[VerticalWell],
        **kwargs: Any,
    ) -> None:
        """Add vertical well markers to the 2D axes.

        Parameters
        ----------
        wells : Sequence[VerticalWell]
            Collection of vertical well instances to render.
        **kwargs : Any
            Additional keyword arguments forwarded to the backend renderer.

        Raises
        ------
        NotImplementedError
            If the backend does not support this feature.
        """
        self._unsupported("add_wells")

    def _unsupported(self, feature: str) -> None:
        """Raise a consistent error for unsupported backend features.

        Parameters
        ----------
        feature : str
            Name of the unsupported feature.

        Raises
        ------
        NotImplementedError
            Always raised with the backend class name and feature name.
        """
        raise NotImplementedError(f"{type(self).__name__} does not support `{feature}`.")
