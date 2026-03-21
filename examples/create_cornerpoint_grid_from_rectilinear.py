from petres.grids.cornerpoint import CornerPointGrid


x = [0, 50, 100, 200, 400, 700, 1000]
y = [0, 100, 300, 600, 1000]
z = [0, 10, 25, 50, 80, 100]

grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)
grid.show()