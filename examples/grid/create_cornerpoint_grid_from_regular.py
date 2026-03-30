from petres.grids.cornerpoint import CornerPointGrid


grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    ni=20,
    nj=20,
    nk=3,
)

print(grid.summary())

grid.show(scalars="active")


# Alternatively, you can specify cell sizes instead of number of cells:
grid = CornerPointGrid.from_regular(
    xlim=(0, 1000),
    ylim=(0, 1000),
    zlim=(0, 100),
    dx=20,
    dy=20,
    dz=33.333333333333336,
)
grid.show()