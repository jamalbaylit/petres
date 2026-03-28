"""
Example: Using Viewer2D with multiple horizons and custom styling

This example demonstrates advanced usage of the 2D matplotlib viewer:
- Adding multiple horizons to the same plot
- Customizing themes and appearance
- Using different visualization options
"""

from petres.models import Horizon
from petres.interpolators import IDWInterpolator
from petres.viewers import Viewer2D, Viewer2DTheme
import numpy as np

# Create sample horizons
xy1 = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
z1 = np.array([100, 105, 110, 102, 106])
horizon1 = Horizon(name="Horizon 1", interpolator=IDWInterpolator(), xy=xy1, z=z1)

xy2 = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
z2 = np.array([120, 125, 130, 122, 126])
horizon2 = Horizon(name="Horizon 2", interpolator=IDWInterpolator(), xy=xy2, z=z2)

# Example 1: Simple horizon view
print("Example 1: Simple horizon view")
horizon1.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50)

# Example 2: Custom theme
print("Example 2: Custom theme with different cmap")
theme = Viewer2DTheme(
    figure_size=(12, 10),
    background="lightgray",
    grid=True,
    grid_alpha=0.5,
    xlabel="Easting (m)",
    ylabel="Northing (m)",
    title="Custom Styled Horizon Map",
    cmap="plasma",
    aspect="equal"
)

viewer = Viewer2D(theme=theme)
viewer.add_horizon(
    horizon1, 
    xlim=(0, 100), 
    ylim=(0, 100), 
    ni=60, 
    nj=60,
    show_contours=True,
    contour_levels=15
)
viewer.show()

# Example 3: Multiple horizons (would need subplots or separate plots)
print("Example 3: Horizon with custom contour levels")
horizon2.show2d(
    xlim=(0, 100), 
    ylim=(0, 100), 
    ni=50, 
    nj=50,
    cmap="terrain",
    contour_levels=20
)

print("All examples complete!")
