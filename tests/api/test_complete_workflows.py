"""API tests for complete end-to-end user workflows."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import BoundaryPolygon, Horizon, VerticalWell, Zone


class TestCompleteGridToPropertyWorkflow:
    """Test complete workflow from grid creation to property modeling."""

    def test_regular_grid_with_constant_property(self):
        """Create regular grid and add constant property."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.2)

        assert grid.n_cells == 10 * 10 * 5
        assert poro.values.shape == grid.shape

    def test_rectilinear_grid_with_stochastic_property(self):
        """Create rectilinear grid and add stochastic property."""
        x = np.linspace(0, 1000, 11)
        y = np.linspace(0, 1000, 11)
        z = np.linspace(0, 100, 6)

        grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill_normal(mean=0.22, std=0.02, seed=42)

        # Shape is (nk, nj, ni) = (len(z)-1, len(y)-1, len(x)-1) = (5, 10, 10)
        assert grid.shape == (5, 10, 10)
        assert np.nanmean(poro.values[grid.active]) > 0

    def test_grid_with_derived_properties(self):
        """Create grid with derived properties."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        # Base property
        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.2)

        # Derived properties
        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.apply(lambda p: 1000 * p**3, source=poro)

        ntg = grid.properties.create("ntg", eclipse_keyword="NTGR")
        ntg.apply(lambda p: 0.85 * (1 - 0.1 * p), source=poro)

        assert perm.values.shape == grid.shape
        assert ntg.values.shape == grid.shape


class TestHorizonZoneGridWorkflow:
    """Test workflow from horizons to zones to grid."""

    def test_create_zones_from_wells(self):
        """Create zones from well tops."""
        wells = [
            VerticalWell(
                name=f"W{i}",
                x=i * 30,
                y=i * 30,
                tops={"Top": 100 + i*5, "Base": 130 + i*5}
            )
            for i in range(3)
        ]

        # Create horizons from well tops using keyword-only arguments
        h_top = Horizon.from_wells(name="Top", wells=wells, interpolator=IDWInterpolator())
        h_base = Horizon.from_wells(name="Base", wells=wells, interpolator=IDWInterpolator())

        zone = Zone("Reservoir", top=h_top, base=h_base).divide(nk=4)

        assert zone is not None

    def test_build_grid_from_zones_and_pillars(self):
        """Build corner-point grid from zones and pillars."""
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

        # Shape is (nk, nj, ni) = (4, 10, 10)
        assert grid.shape == (4, 10, 10)
        assert grid.n_cells == 400

    def test_multiple_zones_stacked_grid(self):
        """Create grid from multiple stacked zones."""
        h1 = Horizon(
            name="Top",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 0, 0, 0],
            interpolator=IDWInterpolator(),
        )

        h2 = Horizon(
            name="Mid",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[20, 20, 20, 20],
            interpolator=IDWInterpolator(),
        )

        h3 = Horizon(
            name="Deep",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[40, 40, 40, 40],
            interpolator=IDWInterpolator(),
        )

        zones = [
            Zone("Upper", top=h1, base=h2).divide(nk=3),
            Zone("Lower", top=h2, base=h3).divide(nk=3),
        ]

        pillars = PillarGrid.from_regular(xlim=(0, 100), ylim=(0, 100), ni=10, nj=10)
        grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)

        # Shape is (nk, nj, ni) = (6, 10, 10)  # 3 layers per zone
        assert grid.shape == (6, 10, 10)


class TestGridBoundaryWorkflow:
    """Test grid workflow with boundary polygon."""

    def test_apply_boundary_and_add_properties(self):
        """Apply boundary to grid and add properties."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=20,
            nj=20,
            nk=5,
        )

        boundary = BoundaryPolygon.from_bbox(25, 25, 75, 75)
        grid.apply_boundary(boundary)

        # Add properties to bounded grid
        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill_normal(mean=0.2, std=0.05, seed=42)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.apply(lambda p: 500 * p**2, source=poro)

        assert grid.n_active < grid.n_cells
        assert poro.values.shape == grid.shape


class TestGridImportExportWorkflow:
    """Test grid lifecycle with import/export."""

    def test_create_export_import_modify_export(self, tmp_path: Path):
        """Create grid, export, import, modify, export again."""
        # Create and export initial grid
        grid1 = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=5,
        )

        poro1 = grid1.properties.create("poro", eclipse_keyword="PORO")
        poro1.fill(0.2)

        file1 = tmp_path / "grid1.grdecl"
        grid1.to_grdecl(file1, properties=["poro"])

        # Import
        grid2 = CornerPointGrid.from_grdecl(file1)

        # Modify
        perm2 = grid2.properties.create("perm", eclipse_keyword="PERMX")
        perm2.fill(100)

        file2 = tmp_path / "grid2.grdecl"
        grid2.to_grdecl(file2, properties=["perm"])

        assert file1.exists()
        assert file2.exists()

    def test_roundtrip_with_boundary(self, tmp_path: Path):
        """Roundtrip grid with applied boundary."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=15,
            nj=15,
            nk=3,
        )

        boundary = BoundaryPolygon.from_bbox(20, 20, 80, 80)
        grid.apply_boundary(boundary)

        file1 = tmp_path / "bounded.grdecl"
        grid.to_grdecl(file1)

        grid_reimported = CornerPointGrid.from_grdecl(file1)

        assert grid_reimported.n_active == grid.n_active
        assert grid_reimported.shape == grid.shape


class TestWellToPropertyWorkflow:
    """Test workflow from well data to property."""

    def test_well_data_to_interpolated_property(self):
        """Create property from well samples using interpolation."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 200),
            ylim=(0, 200),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        # Create wells with samples
        wells = [
            VerticalWell(name="W1", x=0.0, y=0.0),
            VerticalWell(name="W2", x=200.0, y=0.0),
            VerticalWell(name="W3", x=100.0, y=200.0),
        ]

        wells[0].add_sample("poro", value=0.15)
        wells[1].add_sample("poro", value=0.25)
        wells[2].add_sample("poro", value=0.2)

        # Populate property from wells
        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.from_wells(wells, interpolator=IDWInterpolator(power=2.0), source="poro")

        # Derive property from interpolated values
        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.apply(lambda p: 1000 * p**3, source=poro)

        assert np.all(np.isfinite(poro.values[grid.active]))
        assert np.all(np.isfinite(perm.values[grid.active]))


class TestCompleteReservoirModel:
    """Test creation of complete reservoir model."""

    def test_full_reservoir_modeling_workflow(self, tmp_path: Path):
        """Create complete reservoir model from scratch."""
        # 1. Create pillar grid
        pillars = PillarGrid.from_regular(xlim=(0, 1000), ylim=(0, 1000), ni=20, nj=20)

        # 2. Create horizons with well tops
        wells = [
            VerticalWell(name="W1", x=100, y=100, tops={"Top": 1000, "Base": 1050}),
            VerticalWell(name="W2", x=900, y=100, tops={"Top": 1005, "Base": 1055}),
            VerticalWell(name="W3", x=500, y=900, tops={"Top": 1002, "Base": 1052}),
        ]

        # from_wells takes keyword-only arguments
        h_top = Horizon.from_wells(name="Top", wells=wells, interpolator=IDWInterpolator(power=2.0))
        h_base = Horizon.from_wells(name="Base", wells=wells, interpolator=IDWInterpolator(power=2.0))

        # 3. Create zone and divide into layers
        zone = Zone("Reservoir", top=h_top, base=h_base).divide(nk=5)

        # 4. Build corner-point grid
        grid = CornerPointGrid.from_zones(pillars=pillars, zones=[zone])

        # 5. Apply boundary
        boundary = BoundaryPolygon.from_bbox(200, 200, 800, 800)
        grid.apply_boundary(boundary)

        # 6. Create properties
        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill_normal(mean=0.2, std=0.05, seed=42)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.apply(lambda p: 500 * p**2, source=poro)

        ntg = grid.properties.create("ntg", eclipse_keyword="NTGR")
        ntg.fill_uniform(low=0.7, high=1.0, seed=42)

        # 7. Export grid
        output_file = tmp_path / "reservoir_model.grdecl"
        grid.to_grdecl(output_file, properties=["poro", "perm", "ntg"])

        # 8. Reimport and verify
        grid_reimported = CornerPointGrid.from_grdecl(
            output_file,
            properties=["PORO", "PERMX", "NTGR"]
        )

        assert grid_reimported.n_cells == grid.n_cells
        assert grid_reimported.n_active == grid.n_active
