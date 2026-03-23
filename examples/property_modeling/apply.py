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

porosity.fill(0.20)
porosity.show(show_inactive=False)



permeability = grid.properties.create(
    "perm",
    eclipse_keyword="PERM",
    description="Permeability"
)
permeability.apply(lambda poro: 100 * poro**3, source="top")
permeability.show(show_inactive=False)
