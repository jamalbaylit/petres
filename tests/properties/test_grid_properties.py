from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import IDWInterpolator
from petres.models import VerticalWell
from petres.errors import ExistingPropertyNameError


def test_create_property_initializes_full_grid_shape(simple_cornerpoint_grid):
    poro = simple_cornerpoint_grid.properties.create("poro", eclipse_keyword="poro")

    assert poro.shape == simple_cornerpoint_grid.shape
    assert poro.eclipse_keyword == "PORO"


def test_create_duplicate_property_name_raises(simple_cornerpoint_grid):
    simple_cornerpoint_grid.properties.create("poro")
    with pytest.raises(ExistingPropertyNameError, match="already exists"):
        simple_cornerpoint_grid.properties.create("poro")


def test_fill_assigns_constant_to_all_cells(simple_cornerpoint_grid):
    poro = simple_cornerpoint_grid.properties.create("poro")
    poro.fill(0.2)
    np.testing.assert_allclose(poro.values, 0.2)


def test_apply_uses_geometric_source_thickness(simple_cornerpoint_grid):
    ntg = simple_cornerpoint_grid.properties.create("ntg")
    ntg.apply(lambda th: th / 20.0, source="thickness")

    assert np.all(np.isfinite(ntg.values))
    assert np.all(ntg.values > 0.0)


def test_from_array_rejects_shape_mismatch(simple_cornerpoint_grid):
    poro = simple_cornerpoint_grid.properties.create("poro")
    with pytest.raises(ValueError, match="grid shape"):
        poro.from_array(np.zeros((1, 1, 1)))


def test_fill_lognormal_generates_positive_values(simple_cornerpoint_grid):
    perm = simple_cornerpoint_grid.properties.create("perm")
    perm.fill_lognormal(mean=100.0, std=10.0, seed=123)

    assert np.all(perm.values > 0.0)


def test_from_wells_xy_populates_property(simple_cornerpoint_grid, sample_wells):
    poro = simple_cornerpoint_grid.properties.create("poro")
    poro.from_wells(sample_wells, interpolator=IDWInterpolator(power=2.0), source="poro", mode="xy")

    assert np.all(np.isfinite(poro.values[simple_cornerpoint_grid.active]))


def test_from_wells_xyz_rejects_scalar_samples(simple_cornerpoint_grid):
    wells = [VerticalWell(name="W1", x=0.0, y=0.0), VerticalWell(name="W2", x=100.0, y=100.0)]
    for well in wells:
        well.add_sample("poro", 0.2)

    poro = simple_cornerpoint_grid.properties.create("poro")
    with pytest.raises(ValueError, match="without depth values"):
        poro.from_wells(wells, interpolator=IDWInterpolator(), source="poro", mode="xyz")


def test_from_wells_rejects_duplicate_xy_samples(simple_cornerpoint_grid):
    w1 = VerticalWell(name="W1", x=10.0, y=20.0)
    w2 = VerticalWell(name="W2", x=10.0, y=20.0)
    w1.add_sample("poro", value=0.1)
    w2.add_sample("poro", value=0.2)

    poro = simple_cornerpoint_grid.properties.create("poro")
    with pytest.raises(ValueError, match="Duplicate sample locations"):
        poro.from_wells([w1, w2], interpolator=IDWInterpolator(), source="poro", mode="xy")
