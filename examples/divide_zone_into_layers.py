from petres.interpolators import IDWInterpolator
from petres.models import Horizon
import numpy as np





# Example of creating a Zone by shifting a Horizon. Note that the Horizon must have store_picks=True (default) to be able to create a Zone, since the picks are needed to create the second horizon. If store_picks=False, the picks are discarded to save memory, and to_zone() will raise an error since it cannot create the second horizon without the picks.
xy = np.array([[0, 0], [1, 5], [2, 1], [1, 1]])
z = np.array([0, 1, 1, 0])
horizon = Horizon(name="Horizon", interpolator=IDWInterpolator(), xy=xy, depth=z)
horizon.show3d(z_scale=3, x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50), title="Horizon")
zone = horizon.to_zone(name="Zone", depth=2)  # creates a Zone with base shifted 2 units deeper than horizon
zone.show3d(z_scale=3, x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50), title="Zone")
zone.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50))

# Divide the zone into 4 equal layers:
zone.divide(nk=4)
zone.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50))


# Divide the zone into 3 layers with specified thickness fractions in increasing depth order: 
zone.divide(fractions=[0.15, 0.5, 0.35])
zone.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50))


