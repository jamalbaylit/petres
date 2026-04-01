from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pytest

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import BoundaryPolygon, Horizon, VerticalWell, Zone

from tests.fixtures.grid_factory import make_plane_samples, make_rectilinear_vertices


def pytest_collection_modifyitems(items: list[Any]) -> None:
    """Auto-tag tests by folder for selective runs in CI/local workflows."""
    path_to_marker = {
        "integration": pytest.mark.integration,
        "regression": pytest.mark.regression,
        "viewers": pytest.mark.viewer,
        "views": pytest.mark.viewer,
    }

    for item in items:
        path_str = str(item.fspath).replace("\\", "/")
        assigned = False

        for folder, marker in path_to_marker.items():
            if f"/tests/{folder}/" in path_str:
                item.add_marker(marker)
                assigned = True

        if not assigned:
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def rectilinear_vertices():
    return make_rectilinear_vertices(ni=2, nj=2, nk=2)


@pytest.fixture
def simple_pillar_grid(rectilinear_vertices):
    x, y, _ = rectilinear_vertices
    return PillarGrid.from_rectilinear(x=x, y=y, z_top=1000.0, z_bottom=1100.0)


@pytest.fixture
def simple_cornerpoint_grid(rectilinear_vertices):
    x, y, z = rectilinear_vertices
    return CornerPointGrid.from_rectilinear(x=x, y=y, z=z)


@pytest.fixture
def horizon_plane_top():
    xy, z = make_plane_samples()
    return Horizon(name="Top", xy=xy, depth=z, interpolator=IDWInterpolator(power=2.0))


@pytest.fixture
def horizon_plane_base():
    xy, z = make_plane_samples()
    return Horizon(name="Base", xy=xy, depth=z + 30.0, interpolator=IDWInterpolator(power=2.0))


@pytest.fixture
def continuous_zones(horizon_plane_top, horizon_plane_base):
    mid = Horizon(
        name="Mid",
        xy=horizon_plane_top.xy,
        depth=horizon_plane_top.depth + 15.0,
        interpolator=IDWInterpolator(power=2.0),
    )
    deep = Horizon(
        name="Deep",
        xy=horizon_plane_top.xy,
        depth=horizon_plane_top.depth + 45.0,
        interpolator=IDWInterpolator(power=2.0),
    )
    return [
        Zone("Upper", top=horizon_plane_top, base=mid).divide(nk=2),
        Zone("Lower", top=mid, base=deep).divide(nk=2),
    ]


@pytest.fixture
def gap_zones(horizon_plane_top):
    h2 = Horizon(
        name="H2",
        xy=horizon_plane_top.xy,
        depth=horizon_plane_top.depth + 20.0,
        interpolator=IDWInterpolator(power=2.0),
    )
    h3 = Horizon(
        name="H3",
        xy=horizon_plane_top.xy,
        depth=horizon_plane_top.depth + 40.0,
        interpolator=IDWInterpolator(power=2.0),
    )
    h4 = Horizon(
        name="H4",
        xy=horizon_plane_top.xy,
        depth=horizon_plane_top.depth + 65.0,
        interpolator=IDWInterpolator(power=2.0),
    )
    return [
        Zone("ZoneA", top=horizon_plane_top, base=h2).divide(nk=2),
        Zone("ZoneB", top=h3, base=h4).divide(nk=2),
    ]


@pytest.fixture
def grid_from_continuous_zones(simple_pillar_grid, continuous_zones):
    return CornerPointGrid.from_zones(pillars=simple_pillar_grid, zones=continuous_zones)


@pytest.fixture
def grid_from_gap_zones(simple_pillar_grid, gap_zones):
    return CornerPointGrid.from_zones(pillars=simple_pillar_grid, zones=gap_zones)


@pytest.fixture
def boundary_box():
    return BoundaryPolygon.from_bbox(0.0, 0.0, 100.0, 100.0, name="AOI")


@pytest.fixture
def sample_wells():
    wells = [
        VerticalWell(name="W1", x=0.0, y=0.0),
        VerticalWell(name="W2", x=200.0, y=0.0),
        VerticalWell(name="W3", x=0.0, y=200.0),
        VerticalWell(name="W4", x=200.0, y=200.0),
    ]
    values = [0.15, 0.2, 0.25, 0.3]
    for w, v in zip(wells, values, strict=True):
        w.add_sample("poro", value=v)
        w.add_sample("perm", value=100.0 + 1000.0 * v, depth=1050.0)
    return wells


@pytest.fixture
def minimal_grdecl_path() -> Path:
    return Path(__file__).parent / "data" / "models" / "minimal_2x2x1.grdecl"
