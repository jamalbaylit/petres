"""API tests that mirror user-facing tutorial examples."""
from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pytest

from petres.grids import CornerPointGrid
from petres.interpolators import IDWInterpolator, RBFInterpolator
from petres.models import VerticalWell


class TestTutorialMappingWellsToGridCells:
    """Coverage for mapping wells to grid columns tutorial examples."""

    def test_well_indices_for_well_and_xy_tuple(self):
        """Map both VerticalWell and raw (x, y) coordinates to indices."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=3,
        )

        well = VerticalWell("Well-A", x=15, y=25)

        ij_from_well = grid.well_indices(well)
        ij_from_xy = grid.well_indices((15, 25))

        assert ij_from_well is not None
        assert ij_from_xy is not None
        assert ij_from_well == ij_from_xy

    def test_well_indices_returns_none_outside_grid(self):
        """Return None when well is outside the grid footprint."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=10,
            nj=10,
            nk=3,
        )

        assert grid.well_indices((1000, 1000)) is None


class TestTutorialPropertyModelingExamples:
    """Coverage for property-modeling tutorial examples."""

    def test_property_from_array_and_fill_nan(self):
        """Populate values from an array and then fill NaN values."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=6,
            nj=5,
            nk=4,
        )

        porosity = grid.properties.create("poro")

        values = np.full(grid.shape, 0.24)
        porosity.from_array(values)

        assert np.allclose(porosity.values, 0.24)

        porosity.values[0, 0, 0] = np.nan
        porosity.fill_nan(0.0)

        assert not np.isnan(porosity.values).any()

    def test_property_from_wells_default_source_name(self):
        """Interpolate property from well samples using the property name as source."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 200),
            ylim=(0, 200),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=4,
        )

        wells = [
            VerticalWell(name="W1", x=0.0, y=0.0),
            VerticalWell(name="W2", x=200.0, y=0.0),
            VerticalWell(name="W3", x=0.0, y=200.0),
        ]
        wells[0].add_sample("porosity", value=0.15)
        wells[1].add_sample("porosity", value=0.25)
        wells[2].add_sample("porosity", value=0.20)

        porosity = grid.properties.create("porosity")
        porosity.from_wells(wells=wells, interpolator=IDWInterpolator(power=2.0))

        assert np.all(np.isfinite(porosity.values[grid.active]))


class TestTutorialInterpolatorExamples:
    """Coverage for tutorial interpolator examples."""

    def test_idw_common_workflow_fit_predict(self):
        """Run fit/predict workflow with IDW interpolator."""
        X = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0], [100.0, 100.0]])
        y = np.array([10.0, 12.0, 11.5, 13.0])

        interp = IDWInterpolator(power=2.0)
        interp.fit(X, y)

        Q = np.array([[50.0, 50.0], [25.0, 75.0]])
        pred = interp.predict(Q)

        assert pred.shape == (2,)
        assert np.all(np.isfinite(pred))

    def test_rbf_workflow_fit_predict(self):
        """Run fit/predict workflow with RBF interpolator."""
        X = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0], [100.0, 100.0]])
        y = np.array([10.0, 12.0, 11.5, 13.0])

        interp = RBFInterpolator(kernel="linear", smoothing=0.0)
        interp.fit(X, y)

        Q = np.array([[50.0, 50.0], [25.0, 75.0]])
        pred = interp.predict(Q)

        assert pred.shape == (2,)
        assert np.all(np.isfinite(pred))


class TestTutorialGridVisualizationWellExamples:
    """Coverage for tutorial examples showing wells on a grid."""

    @pytest.mark.viewer
    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_well_list(self, mock_show):
        """Visualize grid with wells provided as a list."""
        mock_show.return_value = None

        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )
        well1 = VerticalWell("Well-1", x=10, y=20)
        well2 = VerticalWell("Well-2", x=30, y=40)

        grid.show(wells=[well1, well2])

        assert mock_show.called

    @pytest.mark.viewer
    @patch("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer.show")
    def test_show_grid_with_single_well(self, mock_show):
        """Visualize grid with a single well object."""
        mock_show.return_value = None

        grid = CornerPointGrid.from_regular(
            xlim=(0, 100),
            ylim=(0, 100),
            zlim=(0, 50),
            ni=5,
            nj=5,
            nk=3,
        )
        well = VerticalWell("Well-1", x=10, y=20)

        grid.show(wells=well)

        assert mock_show.called
