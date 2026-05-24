"""Load a GRDECL corner-point grid,visualize it in 3D, and save a screenshot of the rendered view."""

from petres.grids import CornerPointGrid
from petres.models import VerticalWell
from petres.viewers import Viewer3D

# Define the path to the ".GRDECL" file containing the grid data
path = r"https://raw.githubusercontent.com/jamalbaylit/petres/v0.1.0/data/opm/norne/grdecl/norne_with_props.grdecl"

# Import corner-point grid from a ".GRDECL" file, including specified properties
grid = CornerPointGrid.from_grdecl(
    path, 
    properties=["PORO"]
)

# Visualize the grid
viewer = Viewer3D(z_scale=5)
viewer.add_wells(
    [
        VerticalWell("Well 1", x=459900, y=-7322900),
        VerticalWell("Well 2", x=456500, y=-7321300),
    ]
)
viewer.add_grid(grid, scalars="PORO", cmap="viridis")
viewer.show()

# Save the last view as a image
viewer.screenshot(
    "grid.png",
    transparent=False 
)