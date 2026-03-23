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

porosity.add_constant(0.20)
porosity.show(show_inactive=False)



permeability = grid.properties.create(
    "perm",
    eclipse_keyword="PERM",
    description="Permeability"
)
permeability.apply(lambda poro: 100 * poro**3, source=porosity)
permeability.show(show_inactive=False)




porosity.add_normal(mean=0.24, std=0.03, min=0.0, max=0.35)
porosity.show(show_inactive=False)