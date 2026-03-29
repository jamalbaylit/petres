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

# Fill porosity with log-normal distribution
porosity.fill_lognormal(mean=0.24, std=0.03)
porosity.show()

# You can optionally set minimum and maximum limits for the generated log-normal distribution values
porosity.fill_lognormal(mean=0.24, std=0.03, min=0.2, max=0.3)
porosity.show()

# To ensure reproducibility of the random values, you can set a seed for the random number generator
porosity.fill_lognormal(mean=0.24, std=0.03, seed=42)
porosity.show()
