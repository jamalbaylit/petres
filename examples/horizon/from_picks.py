"""Create and visualize a horizon from scattered depth points."""

from petres.models import Horizon
from petres.interpolators import IDWInterpolator

# Create a horizon from scattered depth points
horizon = Horizon(
    name="H1",
    xy=[
        [0, 0],
        [100, 0],
        [100, 100],
        [0, 100],
    ],
    depth=[0, 1, 0, 1],
    interpolator=IDWInterpolator(),
)

# Visualize the horizon
horizon.show(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
)