from petres.models import BoundaryPolygon
from petres.models import VerticalWell
import numpy as np

boundary = BoundaryPolygon(
    name="Boundary", 
    vertices=[[0, 0], [1, 5], [2, 1], [1, 1]]
)

boundary.show()



boundary = BoundaryPolygon.from_bbox(
    xmin=0, ymin=0, xmax=1, ymax=5,
    name="Boundary"
)

well1 = VerticalWell(name="Well 1", x=0.5, y=2.5)
well2 = VerticalWell(name="Well 2", x=1.5, y=3.5)
boundary.show(wells=[well1, well2])