from petres.models import BoundaryPolygon
from petres.viewers import Viewer2D
import numpy as np

# Example 1: Create a simple rectangular boundary
print("Example 1: Simple rectangle")
boundary1 = BoundaryPolygon.from_bbox(
    xmin=0, ymin=0, xmax=100, ymax=80, 
    name="Field Boundary"
)
boundary1.show2d(edgecolor='red', linewidth=3)

# Example 2: Create a custom polygon from vertices
print("Example 2: Custom polygon")
vertices = np.array([
    [10, 10],
    [90, 15],
    [85, 70],
    [15, 75],
    [10, 10]  # Close the polygon
])
boundary2 = BoundaryPolygon(vertices=vertices, name="Reservoir AOI")
boundary2.show2d(
    facecolor='lightgreen',
    edgecolor='darkgreen',
    linewidth=2.5,
    alpha=0.4,
    show_vertices=True
)

# Example 3: Multiple boundaries on the same plot
print("Example 3: Multiple boundaries")
outer = BoundaryPolygon.from_bbox(0, 0, 100, 100, name="License Area")
inner = BoundaryPolygon.from_bbox(20, 20, 80, 80, name="Development Area")

viewer = Viewer2D()
viewer.add_boundary_polygon(
    outer, 
    facecolor='lightblue', 
    edgecolor='blue', 
    linewidth=3,
    alpha=0.2
)
viewer.add_boundary_polygon(
    inner, 
    facecolor='orange', 
    edgecolor='darkorange', 
    linewidth=2,
    alpha=0.3
)
viewer.show()

# Example 4: Boundary with other geological features
print("Example 4: Boundary with horizon overlay")
from petres.models import Horizon
from petres.interpolators import IDWInterpolator

# Create boundary
field_boundary = BoundaryPolygon.from_bbox(0, 0, 100, 100, name="Field")

# Create a horizon
xy = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
z = np.array([100, 105, 110, 102, 106])
horizon = Horizon(name="Top Reservoir", interpolator=IDWInterpolator(), xy=xy, depth=z)

# Plot together
viewer2 = Viewer2D()
viewer2.add_boundary_polygon(
    field_boundary,
    facecolor='none',  # No fill, just outline
    edgecolor='black',
    linewidth=3
)
viewer2.add_horizon(
    horizon,
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
    cmap='terrain',
    show_contours=True
)
viewer2.show()

print("All examples complete!")
