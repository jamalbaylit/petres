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

# Fill porosity with a constant value
porosity.fill(0.20)




# Defining a new property from an existing one using the `apply` method
permeability = grid.properties.create(
    "perm",
    eclipse_keyword="PERM",
    description="Permeability"
)
permeability.apply(lambda poro: 100 * poro**3, source=porosity)
permeability.show()

# You can also use multiple source properties in the apply function
permeability.apply(lambda poro, z: 100 * poro**3+z, source=(porosity, "depth"))
permeability.show()


# Alternatively, you can use a predefined function:
def calc_perm(poro, z):
    return 100 * poro**3+z

permeability.apply(calc_perm, source=(porosity, "depth"))