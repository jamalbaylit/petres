from petres.grids import CornerPointGrid
from petres.models import BoundaryPolygon
import numpy as np

from petres.models.wells import VerticalWell

path = "examples/data/corner_point/Norne.GRDECL"
grid = CornerPointGrid.from_grdecl(path, use_actnum=True)

well1 = VerticalWell("Well-1", x=456000, y=7320000)
well2 = VerticalWell("Well-2", x=456600, y=7321000)


# Multiple wells can be passed as a list, or a single well can be passed directly without wrapping in a list
grid.show(wells=[well1, well2])
grid.show(wells=well1)


i, j = grid.well_indices(well1) 

# Or 

i, j = grid.well_indices((456000, 7320000)) 


print(f"Well indices: i={i}, j={j}")


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
grid.show(wells=well)

