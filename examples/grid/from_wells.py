""" Create a grid from well data """

from petres.models import VerticalWell, Horizon, Zone
from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.viewers import Viewer3D 

#  Define wells with their locations and horizon tops
well_ll = VerticalWell(
    name="Well Left Lower Corner",
    x=0,
    y=0,
    tops={'Horizon 1': 0.0, 'Horizon 2': 45.0, 'Horizon 3': 66.0, 'Horizon 4': 143.0}
)
well_lu = VerticalWell(
    name="Well Left Upper Corner",
    x=0,
    y=100,
    tops={'Horizon 1': 50.5, 'Horizon 2': 91.0, 'Horizon 3': 103.0, 'Horizon 4': 143.0}
)
well_ru = VerticalWell(
    name="Well Right Upper Corner",
    x=140,
    y=100,
    tops={'Horizon 1': 44.0, 'Horizon 2': 72.0, 'Horizon 3': 85.0, 'Horizon 4': 143.0}
)
well_rl = VerticalWell(
    name="Well Right Lower Corner",
    x=140,
    y=0,
    tops={'Horizon 1': 22.0, 'Horizon 2': 49.0, 'Horizon 3': 98.0, 'Horizon 4': 143.0}
)

# Define reservoir extent and grid resolution
xlim = (0, 140)
ylim = (0, 100)
ni = 14
nj = 10

# Create horizons from well tops
h1 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 1", interpolator=IDWInterpolator())
h2 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 2", interpolator=IDWInterpolator())
h3 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 3", interpolator=IDWInterpolator())
h4 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 4", interpolator=IDWInterpolator())

# Visualize horizons
viewer = Viewer3D()
viewer.add_horizons([h1, h2, h3, h4],  xlim=xlim, ylim=ylim, dx=2, dy=2)
viewer.show()

# Create zones from horizons and divide them into layers
z1 = Zone(top=h1, base=h2, name="Zone 1").divide(nk=4)
z2 = Zone(top=h3, base=h4, name="Zone 2").divide(nk=5)

# Visualize zones
viewer.add_zones([z1, z2],  xlim=xlim, ylim=ylim, dx=2, dy=2)
viewer.show()

# Define pillars and create grid from zones
pillars = PillarGrid.from_regular(xlim=xlim, ylim=ylim, ni=ni, nj=nj)
grid = CornerPointGrid.from_zones(
    pillars=pillars,
    zones=[z1, z2],
)

# Visualize grid
grid.show(cmap="petres_r", scalars='depth', z_scale=0.5)

# Export grid to ".GRDECL" format
grid.to_grdecl("grid.grdecl")