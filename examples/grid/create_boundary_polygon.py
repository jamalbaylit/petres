from petres.models.boundary import BoundaryPolygon
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
boundary.show()