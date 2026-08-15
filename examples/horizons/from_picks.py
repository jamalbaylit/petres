"""Create and visualize a horizon from scattered depth points."""

from petres.interpolators import IDWInterpolator
from petres.models import Horizon

# Create a horizon from scattered depth points
horizon = Horizon(
    name="H1",
    xy=[
        [20, 78],
        [70, 80],
        [32, 55],
    ],
    depth=[100, 110, 90],
    interpolator=IDWInterpolator(power=2)
)

# Visualize the horizon
horizon.show(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
    z_scale=2,
)