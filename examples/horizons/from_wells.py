"""Create and visualize a horizon from well tops."""

from petres.interpolators import IDWInterpolator
from petres.models import VerticalWell, Horizon

# Define wells with tops for the horizon
well1 = VerticalWell("W1", x=20, y=78, tops={"H1": 100})
well2 = VerticalWell("W2", x=70, y=80, tops={"H1": 110})
well3 = VerticalWell("W3", x=32, y=55, tops={"H1": 90})

# Create a horizon from well tops
horizon = Horizon.from_wells(
    name="H1",
    wells=[well1, well2, well3],
    interpolator=IDWInterpolator(power=2),
)

# Visualize the horizon
horizon.show(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
    wells=[well1, well2, well3],
    z_scale=2,
)