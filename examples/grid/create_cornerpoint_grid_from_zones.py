from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import Zone, Horizon
from petres.viewers import Viewer3D
import numpy as np

h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], z=[0,1,0,1], interpolator=IDWInterpolator())
h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], z=[2,2,3,3], interpolator=IDWInterpolator())
h3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], z=[5,7,8,4], interpolator=IDWInterpolator())
h4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], z=[11,14,13,12], interpolator=IDWInterpolator())

viewer = Viewer3D()
viewer.add_horizon(h1, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="red")
viewer.add_horizon(h2, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="green")
viewer.add_horizon(h3, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="blue")
viewer.add_horizon(h4, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="purple")
viewer.show()

zones = [
  Zone("Caprock", top=h1, base=h2).divide(fractions=[0.2,0.3,0.5]),
  # Zone("Reservoir", top=h2, base=h3).divide(fractions=[0.2,0.3,0.5]),
  Zone("Base", top=h3, base=h4).divide(nk=3),
]

viewer.add_zones(zones, x=np.linspace(0,100,50), y=np.linspace(0,100,50), cmap="viridis", show_layers=True)
viewer.show()

pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=50, nj=50)
# pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), dx=2, dy=2)
# pillars = PillarGrid.from_rectilinear(x=np.linspace(0,100,50), y=np.linspace(0,100,50), z_top=0, z_bottom=15)

grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)
grid.show(show_inactive=False)
