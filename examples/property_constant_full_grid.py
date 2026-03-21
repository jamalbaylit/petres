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
grid.properties.add_constant("poro", 0.20, eclipse_keyword="PORO")

# Access
porosity = grid.properties["poro"]

print("Min Value:", porosity.min)
print("Max Value:", porosity.max)
print("Mean Value:", porosity.mean)
print("Median Value:", porosity.median)
print("Standard Deviation:", porosity.std)
print("Shape:", porosity.values.shape)