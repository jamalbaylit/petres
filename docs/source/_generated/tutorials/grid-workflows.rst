Grid Workflows
==============

Create, inspect, read, and export corner-point grids.

**Difficulty:** beginner
**Tags:** grid, grdecl

These workflows focus on :class:`petres.grids.CornerPointGrid`
and related grid operations.

Create a corner-point grid from a regular grid
----------------------------------------------

Use this workflow when your model starts from regular x, y, z arrays.

See :class:`petres.grids.CornerPointGrid`.

Regular-grid example
^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/create_cornerpoint_grid_from_regular.py``

Builds a corner-point grid from regular coordinate arrays.

.. code-block:: python

   from petres.grids.cornerpoint import CornerPointGrid
   
   
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   grid.show()
   
   
   
   
   # Alternatively, you can specify cell sizes instead of number of cells:
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       dx=20,
       dy=20,
       dz=33.333333333333336,
   )
   grid.show()

Create a corner-point grid from a rectilinear grid
--------------------------------------------------

Use rectilinear coordinates when spacing varies along one or more axes.

**Source:** ``examples/create_cornerpoint_grid_from_rectilinear.py``

.. code-block:: python

   from petres.grids.cornerpoint import CornerPointGrid
   
   
   x = [0, 50, 100, 200, 400, 700, 1000]
   y = [0, 100, 300, 600, 1000]
   z = [0, 10, 25, 50, 80, 100]
   
   grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)
   grid.show()

Read and export GRDECL grids
----------------------------

Import and export simulator-oriented corner-point grids.

Read a GRDECL grid
^^^^^^^^^^^^^^^^^^

**Source:** ``examples/read_eclipse_grdecl.py``

.. code-block:: python

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
   
       # Alternatively, you can use the Viewer3D directly to also add other features like wells, zones, etc.
       # viewer = Viewer3D()
       # viewer.add_grid(grid).show()
   

Export a grid to GRDECL
^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/export_corner_point_grid_to_eclipse_grdecl_file.py``

.. code-block:: python

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
   
       
