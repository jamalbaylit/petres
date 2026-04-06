"""API tests for grid import/export workflows."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from petres.grids import CornerPointGrid


class TestGridExport:
    """Test grid export to GRDECL format."""

    def test_export_grid_to_grdecl(self, tmp_path: Path):
        """Export a regular grid to GRDECL file."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        output_file = tmp_path / "test_grid.grdecl"
        grid.to_grdecl(output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_export_grid_includes_actnum_by_default(self, tmp_path: Path):
        """Verify that ACTNUM is included by default in export."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        output_file = tmp_path / "grid_with_actnum.grdecl"
        grid.to_grdecl(output_file)

        content = output_file.read_text()
        assert "ACTNUM" in content

    def test_export_grid_without_actnum(self, tmp_path: Path):
        """Export grid without ACTNUM keyword."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        output_file = tmp_path / "grid_no_actnum.grdecl"
        grid.to_grdecl(output_file, include_actnum=False)

        assert output_file.exists()

    def test_export_rectilinear_grid(self, tmp_path: Path):
        """Export a rectilinear grid to GRDECL."""
        x = [0, 100, 300, 500]
        y = [0, 200, 500, 800]
        z = [0, 50, 100]

        grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)

        output_file = tmp_path / "rectilinear_grid.grdecl"
        grid.to_grdecl(output_file)

        assert output_file.exists()


class TestGridImport:
    """Test grid import from GRDECL format."""

    def test_export_import_roundtrip(self, tmp_path: Path):
        """Test exporting and re-importing a grid."""
        grid_original = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=5,
            nj=5,
            nk=3,
        )

        output_file = tmp_path / "roundtrip.grdecl"
        grid_original.to_grdecl(output_file)

        grid_reimported = CornerPointGrid.from_grdecl(output_file)

        assert grid_reimported.shape == grid_original.shape
        assert grid_reimported.n_cells == grid_original.n_cells

    def test_import_without_actnum(self, tmp_path: Path):
        """Import a grid file and ignore ACTNUM."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        output_file = tmp_path / "test_import.grdecl"
        grid.to_grdecl(output_file)

        imported = CornerPointGrid.from_grdecl(output_file, use_actnum=False)

        assert imported is not None
        assert imported.n_cells == grid.n_cells


class TestPropertyExport:
    """Test exporting grid properties."""

    def test_export_property_to_grdecl(self, tmp_path: Path):
        """Export a property to GRDECL format."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=3,
        )

        porosity = grid.properties.create(
            name="poro",
            eclipse_keyword="PORO",
            description="Porosity",
        )
        porosity.fill(0.2)

        output_file = tmp_path / "property.grdecl"
        porosity.to_grdecl(output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "PORO" in content

    def test_export_grid_with_properties(self, tmp_path: Path):
        """Export grid geometry and properties together."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=3,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.22)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.fill(100)

        output_file = tmp_path / "grid_with_props.grdecl"
        grid.to_grdecl(output_file, properties=["poro", "perm"])

        assert output_file.exists()
        content = output_file.read_text()
        assert "PORO" in content
        assert "PERMX" in content

    def test_export_selected_properties(self, tmp_path: Path):
        """Export only selected properties from a grid."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=3,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.22)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.fill(100)

        sat = grid.properties.create("sat", eclipse_keyword="SWAT")
        sat.fill(0.3)

        output_file = tmp_path / "selected_props.grdecl"
        grid.to_grdecl(output_file, properties=["poro", "sat"])

        content = output_file.read_text()
        assert "PORO" in content
        assert "SWAT" in content


class TestPropertyImport:
    """Test importing grid properties."""

    def test_import_properties_from_grdecl(self, tmp_path: Path):
        """Import properties from a GRDECL file."""
        # Create and export a grid with properties
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.2)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.fill(100)

        output_file = tmp_path / "grid_props.grdecl"
        grid.to_grdecl(output_file, properties=["poro", "perm"])

        # Import the grid and properties
        imported = CornerPointGrid.from_grdecl(
            output_file,
            properties=["PORO", "PERMX"]
        )

        assert imported is not None
        assert "PORO" in imported.properties or "poro" in imported.properties
        assert "PERMX" in imported.properties or "perm" in imported.properties

    def test_import_specific_property_keyword(self, tmp_path: Path):
        """Import a specific property by keyword."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.2)

        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        perm.fill(50)

        output_file = tmp_path / "grid_multi_props.grdecl"
        grid.to_grdecl(output_file, properties=["poro", "perm"])

        # Import only porosity
        imported = CornerPointGrid.from_grdecl(output_file, properties=["PORO"])

        assert imported is not None


class TestGridImportExportWorkflow:
    """Test complete import/export workflows."""

    def test_modify_grid_after_import(self, tmp_path: Path):
        """Import grid, modify properties, and export."""
        # Create and export initial grid
        grid1 = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )

        export1 = tmp_path / "grid1.grdecl"
        grid1.to_grdecl(export1)

        # Import grid
        grid2 = CornerPointGrid.from_grdecl(export1)

        # Add property to imported grid
        poro = grid2.properties.create("poro", eclipse_keyword="PORO")
        poro.fill(0.25)

        # Export modified grid
        export2 = tmp_path / "grid2.grdecl"
        grid2.to_grdecl(export2, properties=["poro"])

        assert export2.exists()

    def test_export_import_with_boundary_applied(self, tmp_path: Path):
        """Export grid with applied boundary, then import."""
        from petres.models import BoundaryPolygon

        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=3,
        )

        boundary = BoundaryPolygon.from_bbox(20, 20, 80, 80)
        grid.apply_boundary(boundary)

        output_file = tmp_path / "bounded_grid.grdecl"
        grid.to_grdecl(output_file)

        reimported = CornerPointGrid.from_grdecl(output_file)

        assert reimported.shape == grid.shape
        assert reimported.n_active == grid.n_active
