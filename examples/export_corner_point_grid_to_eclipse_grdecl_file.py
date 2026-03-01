from pathlib import Path

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D



if __name__ == "__main__":
    path = "examples/data/corner_point/SNARK.GRDECL"  
    # path = "projects/SGF/eclipse/include/SGF_R2_1a.GRDECL"  

    # Read the GRDECL file and create a CornerPointGrid
    grid = CornerPointGrid.from_grdecl(path)
    grid.show() 


    save_path = "examples/data/corner_point/EXPORT_TEST.GRDECL"
    grid.to_grdecl(save_path)
    grid = CornerPointGrid.from_grdecl(save_path)  # Read back to verify

    # Visualize grid in 3D viewer
    grid.show() 

    