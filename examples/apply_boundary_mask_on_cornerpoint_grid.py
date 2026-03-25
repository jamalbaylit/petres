from petres.grids import CornerPointGrid
from petres.models import BoundaryPolygon
import numpy as np

path = "examples/data/corner_point/Norne.GRDECL"
grid = CornerPointGrid.from_grdecl(path, use_actnum=True)
grid.show() 
# print(grid.bounds)
boundary = BoundaryPolygon.from_vertices(
    vertices=np.array([
        [453114, 7331119],
        [459386, 7331119],
        [459386, 7315835],
        [453114, 7315835]
    ])
)


grid.apply_boundary(boundary)
grid.show()

