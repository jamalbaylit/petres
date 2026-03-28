from petres.grids import CornerPointGrid
import numpy as np

grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    ni=10,
    nj=10,
    nk=5
)

coord = grid.pillars.to_eclipse_coord()


grid.show(scalars='z')
porosity = grid.properties.create(
    "porosity",
    eclipse_keyword="PORO",
)

porosity.fill_normal(mean=0.2, std=0.05, seed=42)

porosity.show()


grid.to_grdecl("example_grid.grdecl", include_actnum=False)
porosity.to_grdecl("example_porosity.grdecl", include_actnum=False)
