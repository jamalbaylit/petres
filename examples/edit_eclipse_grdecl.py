from pathlib import Path

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D



if __name__ == "__main__":
    
    # You can use either a string path or a Path object
    path = "projects/SGF/eclipse/include/SGF_R2_1a.GRDECL"  
    path = "examples/data/corner_point/SNARK.GRDECL"
    path = "examples/data/corner_point/Norne.GRDECL"
    # or
    path = Path(path)  

    # Read the GRDECL file and create a CornerPointGrid
    grid = CornerPointGrid.from_grdecl(path)

    # Visualize grid in 3D viewer
    grid.show() 

    poro = grid.properties.create(
        "PORO",
        eclipse_keyword="PORO",
        description="Porosity of each grid cell (fraction, 0–1).",
    )
    poro.fill_lognormal(mean=0.2, std=0.05, seed=42)

    perm = grid.properties.create(
        "PERMX",
        eclipse_keyword="PERMX",
        description="Permeability in X direction (mD).",
    )
    perm.apply(
        lambda poro: 100 * poro**3,
        source = poro
    )
    print(grid.properties)
    grid.to_grdecl("examples/data/corner_point/Norne_with_props.GRDECL")
    # Alternatively, you can use the Viewer3D directly to also add other features like wells, zones, etc.
    # viewer = Viewer3D()
    # viewer.add_grid(grid).show()

