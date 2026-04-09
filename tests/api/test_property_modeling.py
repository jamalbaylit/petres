"""API tests for property modeling workflows."""
from __future__ import annotations

import numpy as np
import pytest

from petres.grids import CornerPointGrid
from petres.interpolators import IDWInterpolator
from petres.models import VerticalWell


class TestPropertyCreation:
    """Test property creation on grids."""

    def test_create_simple_property(self):
        """Create a property on a grid."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        porosity = grid.properties.create(
            name="poro",
            eclipse_keyword="PORO",
            description="Porosity",
        )

        assert porosity is not None
        assert porosity.name == "poro"

    def test_access_property_by_name(self):
        """Access a property by name after creation."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        grid.properties.create(name="poro", eclipse_keyword="PORO")
        poro_access = grid.properties["poro"]

        assert poro_access is not None

    def test_create_multiple_properties(self):
        """Create multiple properties on a grid."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        poro = grid.properties.create("poro", eclipse_keyword="PORO")
        perm = grid.properties.create("perm", eclipse_keyword="PERMX")
        sat = grid.properties.create("sat", eclipse_keyword="SWAT")

        assert len([poro, perm, sat]) == 3


class TestPropertyFilling:
    """Test filling properties with values."""

    def test_fill_property_with_constant_value(self):
        """Fill a property with a constant value."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        porosity = grid.properties.create("poro")
        porosity.fill(0.2)

        assert np.allclose(porosity.values[grid.active], 0.2)

    def test_fill_property_with_normal_distribution(self):
        """Fill a property with normally distributed values."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        porosity = grid.properties.create("poro")
        porosity.fill_normal(mean=0.22, std=0.02, seed=42)

        assert porosity.values.shape == grid.shape
        assert np.nanmean(porosity.values[grid.active]) > 0

    def test_fill_property_with_uniform_distribution(self):
        """Fill a property with uniformly distributed values."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=3,
        )

        porosity = grid.properties.create("poro")
        porosity.fill_uniform(low=0.1, high=0.3, seed=42)

        values = porosity.values[grid.active]
        assert np.all(values >= 0.1)
        assert np.all(values <= 0.3)

    def test_fill_property_with_lognormal_distribution(self):
        """Fill a property with lognormally distributed values."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=3,
        )

        permeability = grid.properties.create("perm")
        permeability.fill_lognormal(mean=100, std=50, seed=42)

        assert permeability.values.shape == grid.shape
        assert np.all(permeability.values[grid.active] > 0)


class TestPropertyDerivation:
    """Test deriving properties from other properties."""

    def test_derive_property_from_another_with_lambda(self):
        """Derive permeability from porosity using a lambda function."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        porosity = grid.properties.create("poro", eclipse_keyword="PORO")
        porosity.fill(0.2)

        permeability = grid.properties.create("perm", eclipse_keyword="PERMX")
        permeability.apply(lambda poro: 100 * poro**3, source=porosity)

        assert np.all(np.isfinite(permeability.values[grid.active]))
        assert np.all(permeability.values[grid.active] > 0)

    def test_derive_property_from_source_by_name(self):
        """Derive property using source property name."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        perm = grid.properties.create("perm")
        perm.apply(lambda p: 1000 * p**2, source="poro")

        assert perm.values.shape == grid.shape
        assert np.all(perm.values[grid.active] > 0)

    def test_derive_property_with_named_function(self):
        """Derive property using a named function."""
        def porosity_to_permeability(poro):
            return 1000 * poro**3 + 10

        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        poro = grid.properties.create("poro")
        poro.fill(0.2)

        perm = grid.properties.create("perm")
        perm.apply(porosity_to_permeability, source=poro)

        assert perm.values.shape == grid.shape


class TestPropertyFromWells:
    """Test populating properties from well data."""

    def test_fill_property_from_wells(self):
        """Populate property values from well sample data."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 200),
            ylim=(0, 200),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        wells = [
            VerticalWell(name="W1", x=0.0, y=0.0),
            VerticalWell(name="W2", x=200.0, y=0.0),
            VerticalWell(name="W3", x=0.0, y=200.0),
        ]

        wells[0].add_sample("poro", value=0.15)
        wells[1].add_sample("poro", value=0.25)
        wells[2].add_sample("poro", value=0.2)

        poro = grid.properties.create("poro")
        poro.from_wells(wells, interpolator=IDWInterpolator(power=2.0), source="poro")

        assert np.all(np.isfinite(poro.values[grid.active]))


class TestPropertyArray:
    """Test properties with array-based operations."""

    def test_fill_property_from_numpy_array(self):
        """Fill property from a NumPy array."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=10,
            nj=10,
            nk=5,
        )

        poro = grid.properties.create("poro")

        values = np.full(grid.shape, 0.25)
        poro.values = values

        assert np.allclose(poro.values, 0.25)


class TestPropertyStatistics:
    """Test property statistics and inspection."""

    def test_property_statistics(self):
        """Get statistics about a property."""
        grid = CornerPointGrid.from_regular(
            xlim=(0, 1000),
            ylim=(0, 1000),
            zlim=(0, 100),
            ni=20,
            nj=20,
            nk=3,
        )

        poro = grid.properties.create("poro")
        poro.fill_normal(mean=0.22, std=0.02, seed=42)

        # Properties should have valid values
        assert poro.values.shape == grid.shape
        assert np.nanmin(poro.values) >= 0
