"""Create horizons, build zones, visualize in 3D, and generate a corner-point grid."""

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import Zone, Horizon
from petres.viewers import Viewer3D
import numpy as np

# Create horizons with depth values at given (x,y) locations
horizon1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[0.0,0.6,1.2,0.5], interpolator=IDWInterpolator())
horizon2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[3.0,3.8,4.6,3.9], interpolator=IDWInterpolator())
horizon3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[7.0,8.1,9.2,8.0], interpolator=IDWInterpolator())
horizon4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[12.0,13.4,14.8,13.2], interpolator=IDWInterpolator())

# Define x and y limits and resolution for visualization
x = np.linspace(0,100,50)
y = np.linspace(0,100,50)

# Visualize horizons in 3D
viewer = Viewer3D(z_scale=4)
viewer.add_horizon(horizon1, x=x, y=y, color="red")
viewer.add_horizon(horizon2, x=x, y=y, color="green")
viewer.add_horizon(horizon3, x=x, y=y, color="blue")
viewer.add_horizon(horizon4, x=x, y=y, color="purple")
viewer.show()

# Build zones from horizons
zone1 = Zone("Sandstone", top=horizon1, base=horizon2)
zone2 = Zone("Carbonate", top=horizon3, base=horizon4)

# Divide zones into layers
zone1.divide(fractions=[0.2,0.3,0.5])
zone2.divide(nk=3)

# Visualize zones in 3D
viewer.add_zones(
  [zone1, zone2], 
  x=x, 
  y=y, 
  cmap="rainbow", 
  show_layers=True
)
viewer.show()

# Define pillars for corner-point grid generation
pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=50, nj=50)

# Generate corner-point grid from zones and pillars
grid = CornerPointGrid.from_zones(pillars=pillars, zones=[zone1, zone2])

# Visualize the corner-point grid
grid.show(show_inactive=True, z_scale=4, scalars="active")

# Export the grid to a ".GRDECL" file
grid.to_grdecl("grid.grdecl")