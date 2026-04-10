"""API tests for grid visualization workflows.

Note: Visualization tests are marked with 'viewer' marker and can be skipped
in headless/CI environments to avoid blocking on window creation.
Run with: pytest -m viewer tests/api/test_grid_visualization.py
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import Horizon, Zone


pytestmark = pytest.mark.viewer


class TestGridVisualizationApi:
    """Test grid visualization API (mocked to avoid opening windows)."""

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_simple_grid(self, mock_show):
        """Test show method on a simple grid."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        grid.show()
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_z_scale(self, mock_show):
        """Test show method with vertical scale adjustment."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 10),
            ni=5,
            nj=5,
            nk=3,
        )

        grid.show(z_scale=3)
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_inactive_cells(self, mock_show):
        """Test show method including inactive cells."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        grid.show(show_inactive=True)
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_builtin_scalars(self, mock_show):
        """Test show method with built-in scalar attributes."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        grid.show(scalars="top")
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_active_scalar(self, mock_show):
        """Test show method colored by active/inactive status."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        grid.show(scalars="active")
        assert mock_show.called


class TestPropertyVisualizationApi:
    """Test property visualization API (mocked to avoid opening windows)."""

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_property(self, mock_show):
        """Test show method on a property."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        poro.show()
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_property_with_custom_colormap(self, mock_show):
        """Test show method with custom colormap."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        poro.show(cmap="viridis")
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_property_with_custom_title(self, mock_show):
        """Test show method with custom title."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        poro.show(title="Porosity Distribution")
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_property_with_no_title(self, mock_show):
        """Test show method without title."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        poro.show(title=None)
        assert mock_show.called

    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_property_hide_inactive(self, mock_show):
        """Test show method hiding inactive cells."""
        mock_show.return_value = None
        
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        poro.show(show_inactive=False)
        assert mock_show.called


class TestHorizonVisualizationApi:
    """Test horizon visualization API (mocked to avoid opening windows)."""

    def test_horizon_show_method_exists(self):
        """Verify horizon has show method."""
        import numpy as np
        
        horizon = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        # Should have show method
        assert hasattr(horizon, "show")
        assert callable(horizon.show)


class TestZoneVisualizationApi:
    """Test zone visualization API (mocked to avoid opening windows)."""

    def test_zone_show_methods_exist(self):
        """Verify zone has visualization methods."""
        h1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        h2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[2, 2, 3, 3],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Z1", top=h1, base=h2)

        # Should have visualization methods
        assert hasattr(zone, "show")
        assert callable(zone.show)
        assert hasattr(zone, "show2d")
        assert callable(zone.show2d)
        assert hasattr(zone, "show3d")
        assert callable(zone.show3d)


class TestBoundaryPolygonVisualizationApi:
    """Test boundary polygon visualization API."""

    def test_boundary_show_method_exists(self):
        """Verify boundary polygon has show method."""
        from petres.models import BoundaryPolygon

        boundary = BoundaryPolygon(
            name="Boundary",
            vertices=[[0, 0], [100, 0], [100, 100], [0, 100]]
        )

        # Should have show method
        assert hasattr(boundary, "show")
        assert callable(boundary.show)
