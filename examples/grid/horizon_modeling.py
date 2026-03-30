"""
Horizon usage examples.

This script demonstrates how to:

- Create a Horizon from scattered points
- Create a Horizon from well tops
- Modify well tops
- Compute intersection with wells
- Visualize horizons
- Display multiple horizons in a 3D viewer
"""

from petres.interpolators import IDWInterpolator
from petres.models import Horizon, VerticalWell
from petres.viewers import Viewer3D
import numpy as np


# =============================================================================
# Horizon Creation
# =============================================================================

# Create a Horizon from scattered (x, y, z) points using an interpolator.
horizon1 = Horizon(
    name="H1",
    xy=[[20, 78], [55, 65], [90, 35.5]],
    depth=[100, 110, 90],
    interpolator=IDWInterpolator(),
)

horizon1.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
)

# Note:
# Different interpolators can be used. Refer to the interpolator documentation
# and ensure that a compatible interpolator instance is passed to Horizon.


# -----------------------------------------------------------------------------
# Horizon creation from wells
# -----------------------------------------------------------------------------

# Define wells with horizon tops
well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
well2 = VerticalWell(name="Well 2", x=55, y=65, tops={"Horizon 1": 110})
well3 = VerticalWell(name="Well 3", x=90, y=35.5, tops={"Horizon 1": 90})

# Add additional horizon tops after well creation
well1.add_top(horizon="Horizon 2", depth=140)
well2.add_top(horizon="Horizon 2", depth=125)
well3.add_top(horizon="Horizon 2", depth=110)

# Create a Horizon from wells that contain the specified horizon top
horizon1 = Horizon.from_wells(
    name="Horizon 1",
    wells=[well1, well2, well3],
    interpolator=IDWInterpolator(),
)

horizon1.show(
    x=np.linspace(0, 100, 100),
    y=np.linspace(0, 100, 100),
)

# Compute the intersection depth of the horizon with a well
# (the well does not need to be used during horizon creation)
print(horizon1.intersect(well2))


# -----------------------------------------------------------------------------
# Updating well tops
# -----------------------------------------------------------------------------

# A horizon top cannot be added again if it already exists in a well.
# In such cases, remove the existing top first, then add the new value.
well2.remove_top("Horizon 1")
well2.add_top("Horizon 1", 120)


# =============================================================================
# Horizon Visualization
# =============================================================================

# Horizons are continuous surfaces. For visualization, they are sampled
# at discrete (x, y) locations.

# Option 1: Provide explicit x and y sampling arrays
horizon1.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    view="2d",  # or "3d"
)

# Option 2: Define limits and number of samples
horizon1.show(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
)

# Option 3: Define limits and spacing
horizon1.show(
    xlim=(0, 100),
    ylim=(0, 100),
    dx=2,
    dy=2,
)



# =============================================================================
# Multiple Horizon Visualization
# =============================================================================

horizon2 = Horizon.from_wells(
    name="Horizon 2",
    wells=[well1, well2, well3],
    interpolator=IDWInterpolator(),
)

viewer = Viewer3D()

# Add multiple horizons with a colormap
viewer.add_horizons(
    horizons=[horizon1, horizon2],
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    cmap="viridis",
)
viewer.show()

# Alternatively, assign colors individually
viewer = Viewer3D()

viewer.add_horizon(
    horizon1,
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    color="red",
)

viewer.add_horizon(
    horizon2,
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    color="blue",
)

viewer.show()