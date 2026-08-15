"""Create a regular corner-point grid and visualize it."""

from petres.grids.cornerpoint import CornerPointGrid

# Grid creation
grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    ni=20,
    nj=20,
    nk=3,
)

# Output and visualization
print(grid.summary())

grid.show(
    scalars="depth",
    z_scale=2,
    cmap="petres_r",
)