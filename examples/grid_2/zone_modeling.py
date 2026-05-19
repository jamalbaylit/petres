import numpy as np

from petres.interpolators import IDWInterpolator
from petres.models import Horizon, Zone, VerticalWell
from petres.viewers import Viewer3D


# In Petres, a zone is defined by two horizons: a top horizon and a base horizon.
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

zone1 = Zone(name="Z1", top=horizon1, base=horizon2)


# =====================
# Zone Layering
# =====================

# Zones can be subdivided into multiple layers in several ways.

# Divide the zone into 4 uniform layers.
zone1.divide(nk=4)

# Alternatively, layer thicknesses can be defined using relative fractions.
# Here, the first two layers have equal thickness, and the third layer is
# twice as thick as each of the first two.
zone1.divide(fractions=[1, 1, 2])

# Layer boundaries can also be specified directly using normalized levels.
# Here, the first layer occupies 20% of the total zone thickness, and the
# second layer occupies the remaining 80%.
zone1.divide(levels=[0.0, 0.2, 1.0])


# =====================
# Zone Visualization
# =====================

# Similar to horizons, zones are continuous subsurface surfaces.
# For visualization, they must be sampled on a discrete set of points.
#
# You can provide x and y coordinates directly, and the interpolator
# will compute the corresponding z values.

well1 = VerticalWell(name="Well 1", x=50, y=50)
well2 = VerticalWell(name="Well 2", x=75, y=25)
zone1.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    view="3d",
    wells=[well1, well2]
)
zone1.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    view="2d",
    wells=[well1, well2]
)

# Alternatively, you can define the sampling region using axis limits
# together with the number of sampling points in each direction.
zone1.show(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
    wells=[well1, well2]
)

# You can also define the sampling density using grid spacing
# instead of the number of points.
zone1.show(
    xlim=(0, 100),
    ylim=(0, 100),
    dx=2,
    dy=2,
    wells=[well1, well2]
)


# =====================
# Visualizing Multiple Zones
# =====================

# Multiple zones can also be visualized together using the Viewer3D class.
horizon3 = Horizon(
    name="H3",
    xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
    depth=[5, 7, 8, 4],
    interpolator=IDWInterpolator(),
)

zone2 = Zone(name="Zone 2", top=horizon2, base=horizon3)

viewer = Viewer3D()
viewer.add_zones(
    zones=[zone1, zone2],
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    cmap="viridis",
)
viewer.show()

# Alternatively, colors can be assigned manually for each zone.
viewer = Viewer3D()
viewer.add_zone(
    zone1,
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    color="red",
)
viewer.add_zone(
    zone2,
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    color="blue",
)
viewer.show()