"""API tests for grid creation workflows."""
from __future__ import annotations

import numpy as np
import pytest

from petres.grids import CornerPointGrid, PillarGrid


class TestRectilinearGridCreation:
    """Test rectilinear grid creation workflows."""

    def test_create_simple_rectilinear_grid(self):
        """Create a simple rectilinear grid."""
        x = [0, 50, 100, 200, 400, 700, 1000]
        y = [0, 100, 300, 600, 1000]
        z = [0, 10, 25, 50, 80, 100]

        grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

        assert grid is not None
        # Shape is (nk, nj, ni) where nk=len(z)-1, nj=len(y)-1, ni=len(x)-1
        assert grid.shape == (len(z) - 1, len(y) - 1, len(x) - 1)
        assert grid.n_cells == (len(x) - 1) * (len(y) - 1) * (len(z) - 1)

    def test_rectilinear_grid_with_numpy_arrays(self):
        """Create rectilinear grid using NumPy arrays."""
        x = np.array([0, 100, 300, 500])
        y = np.array([0, 200, 500, 800])
        z = np.array([0, 50, 100])

        grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

        assert grid is not None
        # Shape is (nk, nj, ni) = (len(z)-1, len(y)-1, len(x)-1) = (2, 3, 3)
        assert grid.shape == (2, 3, 3)

    def test_rectilinear_grid_with_linspace(self):
        """Create rectilinear grid using linspace for regular spacing."""
        x = np.linspace(0, 1000, 11)
        y = np.linspace(0, 1000, 11)
        z = np.linspace(0, 100, 6)

        grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

        assert grid is not None
        # Shape is (nk, nj, ni) = (len(z)-1, len(y)-1, len(x)-1) = (5, 10, 10)
        assert grid.shape == (5, 10, 10)


class TestRegularGridCreation:
    """Test regular grid creation workflows."""

    def test_create_regular_grid_by_cell_count(self):
        """Create a regular grid by specifying number of cells."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3
        )

        assert grid is not None
        # Shape is (nk, nj, ni)
        assert grid.shape == (3, 20, 20)
        assert grid.n_cells == 20 * 20 * 3

    def test_create_regular_grid_by_cell_size(self):
        """Create a regular grid by specifying cell sizes."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            dx=50,
            dy=50,
            dz=50
        )

        assert grid is not None
        # Shape is (nk, nj, ni) = (zlim/dz, ylim/dy, xlim/dx) = (2, 20, 20)
        assert grid.shape == (2, 20, 20)

    def test_regular_grid_summary(self):
        """Test that grid summary method works."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5
        )

        summary = grid.summary()
        assert summary is not None

    def test_regular_grid_with_different_cell_counts(self):
        """Create regular grids with different cell counts."""
        grids = [
            CornerPointGrid.from_regular(xlim=(0, 100), ylim=(0, 100), zlim=(0, 50), ni=5, nj=5, nk=2),
            CornerPointGrid.from_regular(xlim=(0, 100), ylim=(0, 100), zlim=(0, 50), ni=10, nj=5, nk=3),
            CornerPointGrid.from_regular(xlim=(0, 100), ylim=(0, 100), zlim=(0, 50), ni=20, nj=20, nk=10),
        ]

        assert len(grids) == 3
        assert grids[0].n_cells < grids[1].n_cells < grids[2].n_cells


class TestPillarGridCreation:
    """Test pillar grid creation workflows."""

    def test_create_regular_pillar_grid(self):
        """Create a regular pillar grid."""
        pillars = PillarGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            ni=50,
            nj=50,
        )

        assert pillars is not None
        # PillarGrid uses cell_shape instead of shape
        assert pillars.cell_shape == (50, 50)

    def test_regular_pillar_grid_with_cell_size(self):
        """Create a regular pillar grid using cell sizes."""
        pillars = PillarGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            dx=2,
            dy=2,
        )

        assert pillars is not None
        # PillarGrid uses cell_shape instead of shape
        assert pillars.cell_shape == (50, 50)

    def test_create_rectilinear_pillar_grid(self):
        """Create a rectilinear pillar grid with non-uniform spacing."""
        x = [0, 10, 50, 70, 100]
        y = np.linspace(0, 100, 50)

        pillars = PillarGrid.from_rectilinear(x=x, y=y)

        assert pillars is not None
        # cell_shape is (nj, ni) = (len(y)-1, len(x)-1)
        assert pillars.cell_shape == (49, 4)

    def test_rectilinear_pillar_grid_with_depth(self):
        """Create rectilinear pillar grid with explicit top and base depths."""
        x = [0, 10, 50, 70, 100]
        y = np.linspace(0, 100, 50)

        pillars = PillarGrid.from_rectilinear(
            x=x,
            y=y,
            top=1000,
            base=1500,
        )

        assert pillars is not None
        # cell_shape is (nj, ni) = (len(y)-1, len(x)-1)
        assert pillars.cell_shape == (49, 4)

    def test_different_pillar_configurations(self):
        """Test creating pillars with different configurations."""
        pillar_configs = [
            {"xlim": (0, 100), "ylim": (0, 100), "ni": 10, "nj": 10},
            {"xlim": (0, 1000), "ylim": (0, 1000), "ni": 20, "nj": 20},
            {"xlim": (0, 500), "ylim": (0, 500), "dx": 50, "dy": 50},
        ]

        pillars_list = [PillarGrid.from_regular(**config) for config in pillar_configs]

        assert len(pillars_list) == 3
        assert all(p is not None for p in pillars_list)
