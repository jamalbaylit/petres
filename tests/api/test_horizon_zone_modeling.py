"""API tests for horizon and zone modeling workflows."""
from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import IDWInterpolator
from petres.models import Horizon, VerticalWell, Zone


class TestHorizonFromPoints:
    """Test horizon creation from sample points."""

    def test_create_horizon_from_sample_points(self):
        """Create a horizon from sample points using IDW interpolation."""
        horizon = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        assert horizon is not None
        assert horizon.name == "H1"
        assert len(horizon.xy) == 4

    def test_create_horizon_with_more_sample_points(self):
        """Create horizon with many sample points."""
        np.random.seed(42)
        xy = np.random.rand(50, 2) * 100
        depth = np.random.rand(50) * 50

        horizon = Horizon(
            name="H2",
            xy=xy,
            depth=depth,
            interpolator=IDWInterpolator(),
        )

        assert horizon is not None
        assert len(horizon.xy) == 50

    def test_horizon_with_different_interpolators(self):
        """Create horizons with different interpolators."""
        xy = [[0, 0], [100, 0], [100, 100], [0, 100]]
        depth = [0, 1, 0, 1]

        # Test with default IDW interpolator
        horizon1 = Horizon(
            name="H1",
            xy=xy,
            depth=depth,
            interpolator=IDWInterpolator(),
        )

        # Test with IDW power parameter
        horizon2 = Horizon(
            name="H2",
            xy=xy,
            depth=depth,
            interpolator=IDWInterpolator(power=3.0),
        )

        assert horizon1 is not None
        assert horizon2 is not None

    def test_evaluate_horizon_at_point(self):
        """Test evaluating horizon at a specific point."""
        horizon = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        # Sample horizon at a point using sample() method
        depth_values = horizon.sample([[50, 50]])
        assert depth_values is not None
        assert isinstance(depth_values, np.ndarray)


class TestHorizonFromWells:
    """Test horizon creation from well tops."""

    def test_create_wells_with_tops(self):
        """Create vertical wells with horizon tops."""
        well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
        well2 = VerticalWell(name="Well 2", x=20, y=78, tops={"Horizon 1": 110})
        well3 = VerticalWell(name="Well 3", x=32, y=55, tops={"Horizon 1": 90})

        assert well1 is not None
        assert well2 is not None
        assert well3 is not None

    def test_add_top_to_well(self):
        """Test adding tops to wells after creation."""
        well = VerticalWell(name="Well 1", x=20, y=78)

        well.add_top("Horizon 1", 100)
        well.add_top("Horizon 2", 150)

        assert well is not None

    def test_create_horizon_from_wells(self):
        """Create a horizon from well tops."""
        well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
        well2 = VerticalWell(name="Well 2", x=50, y=50, tops={"Horizon 1": 110})
        well3 = VerticalWell(name="Well 3", x=32, y=55, tops={"Horizon 1": 90})

        # from_wells takes keyword-only arguments
        horizon = Horizon.from_wells(
            name="Horizon 1",
            wells=[well1, well2, well3],
            interpolator=IDWInterpolator()
        )

        assert horizon is not None
        assert horizon.name == "Horizon 1"

    def test_horizon_well_intersection(self):
        """Test finding where a horizon intersects a well."""
        well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
        well2 = VerticalWell(name="Well 2", x=20, y=78, tops={"Horizon 1": 110})
        well3 = VerticalWell(name="Well 3", x=32, y=55, tops={"Horizon 1": 90})

        horizon = Horizon.from_wells(
            name="Horizon 1",
            wells=[well1, well2, well3],
            interpolator=IDWInterpolator()
        )

        # Get intersection with one of the wells used in interpolation
        intersection = horizon.intersect(well1)
        assert intersection is not None


class TestZoneCreation:
    """Test zone creation from horizons."""

    def test_create_zone_from_two_horizons(self):
        """Create a zone from two horizons."""
        horizon1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        horizon2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[2, 2, 3, 3],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Z1", top=horizon1, base=horizon2)

        assert zone is not None
        assert zone.name == "Z1"

    def test_create_zone_from_single_horizon_with_thickness(self):
        """Create a zone from a single horizon with constant thickness."""
        horizon = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        zone = horizon.to_zone(name="Zone 1", depth=2)

        assert zone is not None
        assert zone.name == "Zone 1"


class TestZoneLayering:
    """Test zone division into layers."""

    def test_divide_zone_uniformly(self):
        """Divide a zone into equal layers."""
        horizon1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        horizon2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[2, 2, 3, 3],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Z1", top=horizon1, base=horizon2)
        zone.divide(nk=4)

        assert zone is not None

    def test_divide_zone_with_fractions(self):
        """Divide zone with relative layer fractions."""
        horizon1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        horizon2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[2, 2, 3, 3],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Z1", top=horizon1, base=horizon2)
        zone.divide(fractions=[1, 1, 2])

        assert zone is not None

    def test_divide_zone_with_levels(self):
        """Divide zone with explicit normalized levels."""
        horizon1 = Horizon(
            name="H1",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[0, 1, 0, 1],
            interpolator=IDWInterpolator(),
        )

        horizon2 = Horizon(
            name="H2",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[2, 2, 3, 3],
            interpolator=IDWInterpolator(),
        )

        zone = Zone(name="Z1", top=horizon1, base=horizon2)
        zone.divide(levels=[0, 0.2, 1])

        assert zone is not None


class TestHorizonZoneWorkflow:
    """Test complete workflows combining horizons and zones."""

    def test_multiple_horizons_to_multiple_zones(self):
        """Create multiple zones from multiple horizons."""
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

        h3 = Horizon(
            name="H3",
            xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
            depth=[4, 4, 5, 5],
            interpolator=IDWInterpolator(),
        )

        zones = [
            Zone("Upper", top=h1, base=h2).divide(nk=2),
            Zone("Lower", top=h2, base=h3).divide(nk=2),
        ]

        assert len(zones) == 2
        assert all(z is not None for z in zones)

    def test_well_tops_to_horizons_to_zones(self):
        """Create zones from horizons derived from well tops."""
        well1 = VerticalWell(name="W1", x=20, y=78, tops={"Horizon 1": 100, "Horizon 2": 130})
        well2 = VerticalWell(name="W2", x=50, y=50, tops={"Horizon 1": 110, "Horizon 2": 140})
        well3 = VerticalWell(name="W3", x=80, y=80, tops={"Horizon 1": 90, "Horizon 2": 120})

        # from_wells takes keyword-only arguments with 'name' parameter
        h1 = Horizon.from_wells(name="Horizon 1", wells=[well1, well2, well3], interpolator=IDWInterpolator())
        h2 = Horizon.from_wells(name="Horizon 2", wells=[well1, well2, well3], interpolator=IDWInterpolator())

        zone = Zone("Reservoir", top=h1, base=h2).divide(nk=3)

        assert zone is not None
