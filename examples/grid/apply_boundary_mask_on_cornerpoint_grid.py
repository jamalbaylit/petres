from petres.grids import CornerPointGrid
from petres.models import BoundaryPolygon
import numpy as np

from petres.models.wells import VerticalWell

path = "examples/data/corner_point/Norne.GRDECL"
grid = CornerPointGrid.from_grdecl(path, use_actnum=True)

well = VerticalWell("A", x=456000, y=7320000)
i, j = grid.well_indices(well) 

# Or 

i, j = grid.well_indices((456000, 7320000)) 


print(f"Well indices: i={i}, j={j}")

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

