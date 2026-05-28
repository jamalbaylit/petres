Grid Generation
===============

Examples for generating and visualizing corner-point grids.

Basic Grid Generation
---------------------

Examples for creating rectilinear and regular corner-point grids.

Generate a Rectilinear Corner-Point Grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Create a corner-point grid from non-uniform 
coordinates.

.. code-block:: python

   """Create and visualize a corner-point grid from rectilinear coordinates."""
   
   from petres.grids.cornerpoint import CornerPointGrid
   
   
   # Define grid coordinates
   x = [0, 50, 100, 200, 400, 700, 1000]
   y = [0, 100, 300, 600, 1000]
   z = [0, 10, 25, 50, 80, 100]
   
   # Create grid from coordinates
   grid = CornerPointGrid.from_rectilinear(
       x=x,
       y=y,
       z=z
   )
   
   # Display results
   print(grid.summary())
   grid.show()

Generate a Regular Grid
^^^^^^^^^^^^^^^^^^^^^^^

Create a regular grid using cell counts or cell dimensions.

.. code-block:: python

   """Create a regular corner-point grid and visualize it."""
   
   from petres.grids.cornerpoint import CornerPointGrid
   
   # Grid creation
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   
   # Output and visualization
   print(grid.summary())
   
   grid.show(
       scalars="depth",
       z_scale=2,
       cmap="petres_r",
   )

Advanced Grid Generation
------------------------

Examples for building grids from horizons, zones, and well data.

Create a Grid from Horizons and Zones
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generate horizons and zones, build a pillar grid, derive a
corner-point grid,.

.. code-block:: python

   """Create horizons, build zones, visualize in 3D, and generate a corner-point grid."""
   
   from petres.grids import CornerPointGrid, PillarGrid
   from petres.interpolators import IDWInterpolator
   from petres.models import Zone, Horizon
   from petres.viewers import Viewer3D
   import numpy as np
   
   # Create horizons with depth values at given (x,y) locations
   horizon1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[0.0,0.6,1.2,0.5], interpolator=IDWInterpolator())
   horizon2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[3.0,3.8,4.6,3.9], interpolator=IDWInterpolator())
   horizon3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[7.0,8.1,9.2,8.0], interpolator=IDWInterpolator())
   horizon4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[12.0,13.4,14.8,13.2], interpolator=IDWInterpolator())
   
   # Define x and y limits and resolution for visualization
   x = np.linspace(0,100,50)
   y = np.linspace(0,100,50)
   
   # Visualize horizons in 3D
   viewer = Viewer3D(z_scale=4)
   viewer.add_horizon(horizon1, x=x, y=y, color="red")
   viewer.add_horizon(horizon2, x=x, y=y, color="green")
   viewer.add_horizon(horizon3, x=x, y=y, color="blue")
   viewer.add_horizon(horizon4, x=x, y=y, color="purple")
   viewer.show()
   
   # Build zones from horizons
   zone1 = Zone("Sandstone", top=horizon1, base=horizon2)
   zone2 = Zone("Carbonate", top=horizon3, base=horizon4)
   
   # Divide zones into layers
   zone1.divide(fractions=[0.2,0.3,0.5])
   zone2.divide(nk=3)
   
   # Visualize zones in 3D
   viewer.add_zones(
     [zone1, zone2], 
     x=x, 
     y=y, 
     cmap="rainbow", 
     show_layers=True
   )
   viewer.show()
   
   # Define pillars for corner-point grid generation
   pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=50, nj=50)
   
   # Generate corner-point grid from zones and pillars
   grid = CornerPointGrid.from_zones(pillars=pillars, zones=[zone1, zone2])
   
   # Visualize the corner-point grid
   grid.show(show_inactive=True, z_scale=4, scalars="active")
   
   # Export the grid to a ".GRDECL" file
   grid.to_grdecl("grid.grdecl")

Build a Grid from Well Tops and Horizons
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interpolate horizons from well tops, assemble zones, generate a
corner-point grid.

.. code-block:: python

   """ Create a grid from well data """
   
   from petres.models import VerticalWell, Horizon, Zone, wells
   from petres.grids import CornerPointGrid, PillarGrid
   from petres.interpolators import IDWInterpolator
   from petres.viewers import Viewer3D 
   
   #  Define wells with their locations and horizon tops
   well_ll = VerticalWell(
       name="Well Left Lower Corner",
       x=0,
       y=0,
       tops={'Horizon 1': 0.0, 'Horizon 2': 45.0, 'Horizon 3': 66.0, 'Horizon 4': 143.0}
   )
   well_lu = VerticalWell(
       name="Well Left Upper Corner",
       x=0,
       y=100,
       tops={'Horizon 1': 50.5, 'Horizon 2': 91.0, 'Horizon 3': 103.0, 'Horizon 4': 143.0}
   )
   well_ru = VerticalWell(
       name="Well Right Upper Corner",
       x=140,
       y=100,
       tops={'Horizon 1': 44.0, 'Horizon 2': 72.0, 'Horizon 3': 85.0, 'Horizon 4': 143.0}
   )
   well_rl = VerticalWell(
       name="Well Right Lower Corner",
       x=140,
       y=0,
       tops={'Horizon 1': 22.0, 'Horizon 2': 49.0, 'Horizon 3': 98.0, 'Horizon 4': 143.0}
   )
   
   # Define reservoir extent and grid resolution
   xlim = (0, 140)
   ylim = (0, 100)
   ni = 14
   nj = 10
   
   # Create horizons from well tops
   h1 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 1", interpolator=IDWInterpolator())
   h2 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 2", interpolator=IDWInterpolator())
   h3 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 3", interpolator=IDWInterpolator())
   h4 = Horizon.from_wells(wells=[well_ll, well_lu, well_ru, well_rl], name="Horizon 4", interpolator=IDWInterpolator())
   
   # Visualize horizons
   viewer = Viewer3D(z_scale=0.2)
   viewer.add_horizons([h1, h2, h3, h4],  xlim=xlim, ylim=ylim, dx=2, dy=2)
   viewer.add_wells([well_ll, well_lu, well_ru, well_rl])
   viewer.show()
   
   # Create zones from horizons and divide them into layers
   z1 = Zone(top=h1, base=h2, name="Zone 1").divide(nk=4)
   z2 = Zone(top=h3, base=h4, name="Zone 2").divide(nk=5)
   
   # Visualize zones
   viewer.add_zones([z1, z2],  xlim=xlim, ylim=ylim, dx=2, dy=2)
   viewer.show()
   
   # Define pillars and create grid from zones
   pillars = PillarGrid.from_regular(xlim=xlim, ylim=ylim, ni=ni, nj=nj)
   grid = CornerPointGrid.from_zones(
       pillars=pillars,
       zones=[z1, z2],
   )
   
   # Visualize grid
   grid.show(cmap="petres_r", scalars='depth', z_scale=0.5)
   
   # Get well indices in the grid
   for well in [well_ll, well_lu, well_ru, well_rl]:
       well_indices = grid.well_indices(well)
       print(f"'{well.name}' is located at grid indices (i, j): {well_indices}")
   
   # Export grid to ".GRDECL" format
   grid.to_grdecl("grid.grdecl")
