from petres.models import Horizon, VerticalWell
from petres.interpolators import IDWInterpolator
import numpy as np

well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
well2 = VerticalWell(name="Well 2", x=20, y=78)
well3 = VerticalWell(name="Well 3", x=32, y=55, tops={"Horizon 1": 90})

# Alternatively, you can add horizon picks to the wells after creation:
well1.add_top("Horizon 2", 100)
well2.add_top("Horizon 2", 110)
well3.add_top("Horizon 2", 90)  

# You can create a Horizon directly from the wells, as long as the wells have tops for the given horizon.
horizon = Horizon.from_wells(
    name="Horizon 1",
    wells=[well1, well3],
    interpolator=IDWInterpolator()
)

# Show in 2D using matplotlib
horizon.show2d(x=np.linspace(0, 100, 100), y=np.linspace(0, 100, 100))
