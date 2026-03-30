from petres.eclipse.aquifers import AQUANCONGenerator, AquiferDirection
from petres.grids import CornerPointGrid




if __name__ == "__main__":
    # path = "projects/SNARK_CUSTOM_AQUIFER/include/SNARK.GRDECL" 
    path = "projects/SGF/eclipse/include/SGF_R2_1a.GRDECL" 
    grid = CornerPointGrid.from_grdecl(path)
    grid.show()

    aquifer_generator = AQUANCONGenerator(grid)
    aquifer_generator= (aquifer_generator
        .add_aquifer(1, AquiferDirection.J_PLUS)
        .add_aquifer(1, AquiferDirection.I_PLUS)
        .add_aquifer(1, AquiferDirection.J_MINUS)
        .add_aquifer(1, AquiferDirection.I_MINUS)
    )
    # Generate the aquifer properties
    aquifer_generator.export("projects/SGF/eclipse/include/AQUIFER.INC")
