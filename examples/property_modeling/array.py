from petres.grids import CornerPointGrid
import numpy as np

# Create grid
grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    ni=20,
    nj=20,
    nk=3,
)

# Assign constant porosity to whole grid
porosity = grid.properties.create(
    "poro",
    eclipse_keyword="PORO",
    description="Porosity"
)

# Provide already created distribution of porosity values directly from a numpy array
array = np.full(grid.shape, 0.24)  # Create an array filled with the constant value
porosity.from_array(array)  # Fill the property with the constant value
porosity.show()

# If you want to affect only a specific zone, you can use the `zone` argument to specify the target zone (if zone data is available in the grid)
porosity.from_array(array, zone="zone1")  # Fill the property with the constant value
porosity.show()