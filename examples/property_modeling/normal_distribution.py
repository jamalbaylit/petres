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

# Fill porosity with normal distribution
porosity.fill_normal(mean=0.24, std=0.03)
porosity.show(title="Porosity with Normal Distribution")

# You can optionally set minimum and maximum limits for the generated normal distribution values
porosity.fill_normal(mean=0.24, std=0.03, min=0.2, max=0.3)
porosity.show()

# To ensure reproducibility of the random values, you can set a seed for the random number generator
porosity.fill_normal(mean=0.24, std=0.03, seed=42)
porosity.show()
