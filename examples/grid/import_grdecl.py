""" Import a corner-point grid from a ".GRDECL" file """

from petres.grids import CornerPointGrid

# Define the path to the ".GRDECL" file containing the grid data
path = r"https://raw.githubusercontent.com/jamalbaylit/petres/v0.1.0/data/opm/norne/grdecl/norne_with_props.grdecl"

# Import corner-point grid from a ".GRDECL" file, including specified properties
grid = CornerPointGrid.from_grdecl(
    path, 
    properties=["PORO", "PERMX"]
)

# Visualize the grid
grid.show(scalars="depth", z_scale=5)

# Visualize porosity property
grid.show(scalars="PORO", z_scale=5)
