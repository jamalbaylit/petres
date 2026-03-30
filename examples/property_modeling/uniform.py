from petres.grids import CornerPointGrid
import numpy as np

# Create grid
grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    ni=204,
    nj=20*4,
    nk=3*4,
)

porosity = grid.properties.create(name="poro", eclipse_keyword="PORO", description="Porosity")

# Fill porosity with uniform distribution between given low and high values
porosity.fill_uniform(low=0.24, high=0.3)
porosity.show()

