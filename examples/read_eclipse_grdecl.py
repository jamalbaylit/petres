from pathlib import Path

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D



if __name__ == "__main__":
    
    # You can use either a string path or a Path object
    path = "projects/SGF/eclipse/include/SGF_R2_1a.GRDECL"  
    path = "examples/data/corner_point/SNARK.GRDECL"
    # path = "examples/data/corner_point/Norne.GRDECL"
    # path = "examples/data/corner_point/Norne_with_props.GRDECL"
    # or
    path = Path(path)  
    # Read the GRDECL file and create a CornerPointGrid
    # grid = CornerPointGrid.from_grdecl(path, properties=["PORO", "PERMX"])
    grid = CornerPointGrid.from_grdecl(path)
    # Visualize grid in 3D viewer
    grid.show(show_inactive=False, scalars="depth")





    # Alternatively, you can use the Viewer3D directly to also add other features like wells, zones, etc.
    # viewer = Viewer3D()
    # viewer.add_grid(grid).show()

