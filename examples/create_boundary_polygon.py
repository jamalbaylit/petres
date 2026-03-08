from petres.models.boundary import BoundaryPolygon
import numpy as np

boundary = BoundaryPolygon(name="Boundary", xy=np.array([[0, 0], [1, 5], [2, 1], [1, 1]]))
boundary.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50), color="cyan")