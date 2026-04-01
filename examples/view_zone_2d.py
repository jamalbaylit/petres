from petres.models import Horizon, Zone
from petres.interpolators import IDWInterpolator
from petres.viewers import Viewer2D
import numpy as np

# Create two horizons
xy1 = np.array([[0, 0], [100, 0], [100, 100], [0, 100], [50, 50]])
z1 = np.array([100, 110, 120, 105, 108])
horizon1 = Horizon(name="Top", interpolator=IDWInterpolator(), xy=xy1, depth=z1)

xy2 = np.array([[0, 0], [100, 0], [100, 100], [0, 100], [50, 50]])
z2 = np.array([150, 160, 170, 155, 158])
horizon2 = Horizon(name="Base", interpolator=IDWInterpolator(), xy=xy2, depth=z2)

# Create a zone from the horizons
zone = Zone(name="Reservoir", top=horizon1, base=horizon2)

# Show the zone in 2D with top and base contours
zone.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50)

# Or show thickness map
# zone.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50, show_thickness=True, 
#             show_top=False, show_base=False)

# Or use the Viewer2D directly for more control
# viewer = Viewer2D()
# viewer.add_zone(zone, xlim=(0, 100), ylim=(0, 100), ni=50, nj=50, 
#                 show_thickness=True, show_top=False, show_base=False,
#                 cmap='plasma')
# viewer.show()
