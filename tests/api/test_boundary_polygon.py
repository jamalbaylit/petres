"""API tests for boundary polygon workflows."""
from __future__ import annotations

import pytest

from petres.grids import CornerPointGrid, PillarGrid
from petres.models import BoundaryPolygon, Horizon, Zone 
from petres.interpolators import IDWInterpolator


class TestBoundaryPolygonCreation:
    """Test boundary polygon creation."""

    def test_create_boundary_from_vertices(self):
        """Create a boundary polygon from vertices."""
        boundary = BoundaryPolygon(
            name="Boundary",
            vertices=[[0, 0], [1, 5], [2, 1], [1, 1]]
        )

        assert boundary is not None
        assert boundary.name == "Boundary"

    def test_create_boundary_from_bbox(self):
        """Create a rectangular boundary polygon from bounding box."""
        boundary = BoundaryPolygon.from_bbox(
            xmin=0, ymin=0, xmax=1, ymax=5,
            name="BBox Boundary"
        )

        assert boundary is not None
        assert boundary.name == "BBox Boundary"

    def test_boundary_polygon_with_many_vertices(self):
        """Create boundary polygon with many vertices."""
        vertices = [
            [0, 0], [10, 0], [20, 5], [30, 0],
            [30, 20], [20, 25], [10, 20], [5, 15]
        ]

        boundary = BoundaryPolygon(name="Complex", vertices=vertices)

        assert boundary is not None
        # BoundaryPolygon auto-closes the ring, so vertices are input + 1 (closure point)
        assert len(boundary.vertices) == len(vertices) + 1


class TestBoundaryApplicationToGrid:
    """Test applying boundary polygon to grids."""

    def test_apply_boundary_to_regular_grid(self):
        """Apply boundary polygon to a regular grid."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=5
        )

        boundary = BoundaryPolygon.from_bbox(
            xmin=10, ymin=10, xmax=90, ymax=90,
            name="Test Boundary"
        )

        grid.apply_boundary(boundary)

        assert grid is not None
        assert grid.n_active < grid.n_cells

    def test_boundary_reduces_active_cells(self):
        """Verify that boundary application reduces active cells."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=20,
            nj=20,
            nk=5
        )

        n_before = grid.n_active

        boundary = BoundaryPolygon.from_bbox(
            xmin=25, ymin=25, xmax=75, ymax=75,
            name="Inner Boundary"
        )

        grid.apply_boundary(boundary)

        assert grid.n_active < n_before

    def test_apply_different_boundaries_sequentially(self):
        """Apply different boundaries to the same grid."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=5
        )

        boundary1 = BoundaryPolygon.from_bbox(0, 0, 100, 100)
        boundary2 = BoundaryPolygon.from_bbox(20, 20, 80, 80)

        grid.apply_boundary(boundary1)
        n_after_b1 = grid.n_active

        grid.apply_boundary(boundary2)
        n_after_b2 = grid.n_active

        assert n_after_b1 >= n_after_b2


class TestBoundaryPolygonWithZones:
    """Test boundary polygon with zone-based grids."""

    def test_boundary_on_zone_based_grid(self):
        """Apply boundary to a grid created from zones."""
        h1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        h2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[20, 21, 20, 21],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Reservoir", top=h1, base=h2).divide(nk=4)

        pillars = PillarGrid.from_regular(xlim=(0, 100), ylim=(0, 100), ni=10, nj=10)
        grid = CornerPointGrid.from_zones(pillars=pillars, zones=[zone])

        boundary = BoundaryPolygon.from_bbox(20, 20, 80, 80)
        grid.apply_boundary(boundary)

        assert grid is not None
        assert grid.n_active < grid.n_cells
