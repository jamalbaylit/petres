from petres.interpolators import IDWInterpolator
from petres.viewers import Viewer3D
from petres.models import Horizon, Zone
import numpy as np





# Example of creating a Zone by shifting a Horizon. Note that the Horizon must have store_picks=True (default) to be able to create a Zone, since the picks are needed to create the second horizon. If store_picks=False, the picks are discarded to save memory, and to_zone() will raise an error since it cannot create the second horizon without the picks.
xy = np.array([[0, 0], [1, 5], [2, 1], [1, 1]])
z = np.array([0, 1, 1, 0])
horizon1 = Horizon(name="Horizon 1", interpolator=IDWInterpolator(), xy=xy, z=z)
zone = horizon1.to_zone(name="Zone 1", depth=2)  # creates a Zone with base shifted 5 units deeper than horizon1
zone.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50), color="blue")


# You can also create the second horizon manually and then create the Zone:
z = np.array([5, 2, 4, 1])  # different z values for the second horizon
horizon2 = Horizon(name="Horizon 2", interpolator=IDWInterpolator(), xy=xy, z=z)
zone1 = Zone(name="Zone 1", top=horizon1, base=horizon2)
zone1.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50), color="tan")



