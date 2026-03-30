from petres.models.boundary import BoundaryPolygon
import numpy as np

boundary = BoundaryPolygon(
    name="Boundary", 
    vertices=[[0, 0], [1, 5], [2, 1], [1, 1]]
)
boundary.show()