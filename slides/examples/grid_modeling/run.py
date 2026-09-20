"""Runnable companion to the "Grid Modeling" deck (main.py).

Builds the H1/H2 horizons the deck's snippets refer to, wraps them in a zone,
and grids the result -- so the screenshots in assets/ come from real output.

The structure is a doubly-plunging anticline striking NE, with a secondary
dome on its southeast flank and a saddle between the two. The reservoir
interval thins over the crest, so the layering fans out on the flanks.
"""

import numpy as np

from petres.interpolators import RBFInterpolator
from petres.models import Horizon, Zone

# ---------------------------------------------------------------------------
# Structural model
# ---------------------------------------------------------------------------

STRIKE = np.deg2rad(35.0)  # anticline axis azimuth


def _along_axis(x, y):
    """Rotate into (along-axis, across-axis) coordinates centred on the field."""
    dx, dy = x - 50.0, y - 50.0
    cos_a, sin_a = np.cos(STRIKE), np.sin(STRIKE)
    return dx * cos_a + dy * sin_a, -dx * sin_a + dy * cos_a


def top_depth(x, y):
    """Depth to H1 -- the top of the reservoir. Deeper is a larger value."""
    along, across = _along_axis(x, y)

    regional_dip = 2000.0 + 0.55 * x + 0.30 * y
    # Ridge across strike, plunging at both ends -> a four-way closure.
    crest = -85.0 * np.exp(-((across / 17.0) ** 2)) * np.exp(-((along / 62.0) ** 4))
    # Secondary dome on the southeast flank, separated by a saddle.
    dome = -46.0 * np.exp(-(((x - 80.0) / 15.0) ** 2 + ((y - 22.0) / 13.0) ** 2))
    rugosity = 5.0 * np.sin(x / 14.0) * np.cos(y / 12.0)

    return regional_dip + crest + dome + rugosity


def base_depth(x, y):
    """Depth to H2 -- the base of the reservoir, thinned over the crest."""
    _, across = _along_axis(x, y)
    thickness = 46.0 - 17.0 * np.exp(-((across / 21.0) ** 2)) + 6.0 * np.sin(y / 26.0)
    return top_depth(x, y) + thickness


# ---------------------------------------------------------------------------
# Horizons: sample the structure as scattered picks, then reinterpolate
# ---------------------------------------------------------------------------

rng = np.random.default_rng(7)
nodes = np.linspace(4.0, 96.0, 9)
xy = np.stack(np.meshgrid(nodes, nodes), axis=-1).reshape(-1, 2)
xy += rng.uniform(-3.5, 3.5, size=xy.shape)  # jitter, so picks look picked

h1 = Horizon(
    name="H1",
    xy=xy,
    depth=top_depth(xy[:, 0], xy[:, 1]),
    interpolator=RBFInterpolator(kernel="thin_plate_spline", smoothing=0.5),
)

h2 = Horizon(
    name="H2",
    xy=xy,
    depth=base_depth(xy[:, 0], xy[:, 1]),
    interpolator=RBFInterpolator(kernel="thin_plate_spline", smoothing=0.5),
)

# ---------------------------------------------------------------------------
# Zone and grid (the deck's STEP 01 - STEP 03)
# ---------------------------------------------------------------------------
z_scale = 0.3

from petres.viewers import Viewer3D

zone = Zone(
    name="Reservoir",
    top=h1,
    base=h2,
)

# `divide` returns a new Zone -- it does not mutate in place.
zone = zone.divide(nk=4)

# zone.show(
#     x=np.linspace(0, 100, 50),
#     y=np.linspace(0, 100, 50),
#     z_scale=z_scale,
# )
viewer = Viewer3D(z_scale=z_scale)
viewer.add_zone(zone, x=np.linspace(0, 100, 50), y=np.linspace(0, 100, 50))
viewer.show()
# viewer.screenshot("./assets/zone.png", transparent=True)

from petres.grids import PillarGrid

pillars = PillarGrid.from_regular(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
)
from petres.grids import CornerPointGrid
viewer = Viewer3D(z_scale=25)
viewer.add_pillars(pillars)
viewer.show()
# viewer.screenshot("./assets/pillars.png", transparent=True)


grid = CornerPointGrid.from_zones(
    pillars=pillars,
    zones=[zone],
)
# grid.show(z_scale=z_scale)



from petres.viewers import Viewer3DTheme
viewer = Viewer3D(z_scale=z_scale, theme=Viewer3DTheme(
    show_orientation_widget = False,
    show_coordinate_axes = False
))
viewer.add_grid(grid, scalars='thickness', show_colorbar=False)
viewer.show()
viewer.screenshot("./assets/grid.png", transparent=True)
