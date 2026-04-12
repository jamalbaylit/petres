from pathlib import Path

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D



if __name__ == "__main__":
    path = "data/opm/norne/grdecl/norne.grdecl"  
    # path = "projects/SGF/eclipse/include/SGF_R2_1a.GRDECL"  

    # Read the GRDECL file and create a CornerPointGrid
    grid = CornerPointGrid.from_grdecl(path)
    grid.show() 


    save_path = "data/opm/norne/grdecl/export_test.grdecl"
    grid.to_grdecl(save_path)
    grid = CornerPointGrid.from_grdecl(save_path)  # Read back to verify

    # Visualize grid in 3D viewer
    grid.show() 

    