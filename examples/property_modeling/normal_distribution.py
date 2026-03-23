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


porosity = grid.properties.create(name="poro", eclipse_keyword="PORO", description="Porosity")

# porosity.add_normal(mean=0.24, std=0.03, min=0.0, max=0.35)
porosity.show(show_inactive=False)