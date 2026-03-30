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
    name="poro",
    eclipse_keyword="PORO",
    description="Porosity"
)

porosity.fill(0.20)

# ==================
# Vizualize porosity
# ==================
porosity.show()

# You can enable to show inactive cells in the visualization if needed
porosity.show(show_inactive=True)

# You can define a custom colormap for better visualization of porosity distribution
# It expects a valid Matplotlib colormap name (e.g., 'viridis', 'plasma', 'coolwarm', etc.)
porosity.show(cmap='viridis')




# Accessing property statistics
print("Min Value:", porosity.min)
print("Max Value:", porosity.max)
print("Mean Value:", porosity.mean)
print("Median Value:", porosity.median)
print("Standard Deviation:", porosity.std)

# Or get a full summary of the property statistics
print(porosity.summary())

