from petres.interpolators import IDWInterpolator
from petres.viewers import Viewer3D
from petres.models import Horizon
import numpy as np

xy = np.array([[0, 0], [1, 5], [2, 1], [1, 1]])
z = np.array([0, 1, 1, 0])
horizon1 = Horizon(name="Horizon 1", interpolator=IDWInterpolator(), xy=xy, z=z)
horizon1.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50))

# Or directly via Viewer3D:
viewer = Viewer3D()
viewer.add_horizon(horizon1, xlim=(0, 5), ylim=(0, 5), ni=50, nj=50)
viewer.show()
