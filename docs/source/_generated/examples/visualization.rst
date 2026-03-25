Visualization
=============

Focused visualization examples for 2D workflows.

**Difficulty:** beginner
**Tags:** visualization, 2d

These examples show different 2D visualization patterns.

View boundaries and zones in 2D
-------------------------------

Basic 2D visualization examples.

View a boundary in 2D
^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/view_boundary_2d.py``

.. code-block:: python

   from petres.models import BoundaryPolygon
   from petres.viewers import Viewer2D
   import numpy as np
   
   # Example 1: Create a simple rectangular boundary
   print("Example 1: Simple rectangle")
   boundary1 = BoundaryPolygon.from_bbox(
       xmin=0, ymin=0, xmax=100, ymax=80, 
       name="Field Boundary"
   )
   boundary1.show2d(edgecolor='red', linewidth=3)
   
   # Example 2: Create a custom polygon from vertices
   print("Example 2: Custom polygon")
   vertices = np.array([
       [10, 10],
       [90, 15],
       [85, 70],
       [15, 75],
       [10, 10]  # Close the polygon
   ])
   boundary2 = BoundaryPolygon(vertices=vertices, name="Reservoir AOI")
   boundary2.show2d(
       facecolor='lightgreen',
       edgecolor='darkgreen',
       linewidth=2.5,
       alpha=0.4,
       show_vertices=True
   )
   
   # Example 3: Multiple boundaries on the same plot
   print("Example 3: Multiple boundaries")
   outer = BoundaryPolygon.from_bbox(0, 0, 100, 100, name="License Area")
   inner = BoundaryPolygon.from_bbox(20, 20, 80, 80, name="Development Area")
   
   viewer = Viewer2D()
   viewer.add_boundary_polygon(
       outer, 
       facecolor='lightblue', 
       edgecolor='blue', 
       linewidth=3,
       alpha=0.2
   )
   viewer.add_boundary_polygon(
       inner, 
       facecolor='orange', 
       edgecolor='darkorange', 
       linewidth=2,
       alpha=0.3
   )
   viewer.show()
   
   # Example 4: Boundary with other geological features
   print("Example 4: Boundary with horizon overlay")
   from petres.models import Horizon
   from petres.interpolators import IDWInterpolator
   
   # Create boundary
   field_boundary = BoundaryPolygon.from_bbox(0, 0, 100, 100, name="Field")
   
   # Create a horizon
   xy = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
   z = np.array([100, 105, 110, 102, 106])
   horizon = Horizon(name="Top Reservoir", interpolator=IDWInterpolator(), xy=xy, z=z)
   
   # Plot together
   viewer2 = Viewer2D()
   viewer2.add_boundary_polygon(
       field_boundary,
       facecolor='none',  # No fill, just outline
       edgecolor='black',
       linewidth=3
   )
   viewer2.add_horizon(
       horizon,
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
       cmap='terrain',
       show_contours=True
   )
   viewer2.show()
   
   print("All examples complete!")

View a zone in 2D
^^^^^^^^^^^^^^^^^

**Source:** ``examples/view_zone_2d.py``

.. code-block:: python

   from petres.models import Horizon, Zone
   from petres.interpolators import IDWInterpolator
   from petres.viewers import Viewer2D
   import numpy as np
   
   # Create two horizons
   xy1 = np.array([[0, 0], [100, 0], [100, 100], [0, 100], [50, 50]])
   z1 = np.array([100, 110, 120, 105, 108])
   horizon1 = Horizon(name="Top", interpolator=IDWInterpolator(), xy=xy1, z=z1)
   
   xy2 = np.array([[0, 0], [100, 0], [100, 100], [0, 100], [50, 50]])
   z2 = np.array([150, 160, 170, 155, 158])
   horizon2 = Horizon(name="Base", interpolator=IDWInterpolator(), xy=xy2, z=z2)
   
   # Create a zone from the horizons
   zone = Zone(name="Reservoir", top=horizon1, base=horizon2)
   
   # Show the zone in 2D with top and base contours
   zone.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50)
   
   # Or show thickness map
   # zone.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50, show_thickness=True, 
   #             show_top=False, show_base=False)
   
   # Or use the Viewer2D directly for more control
   # viewer = Viewer2D()
   # viewer.add_zone(zone, xlim=(0, 100), ylim=(0, 100), ni=50, nj=50, 
   #                 show_thickness=True, show_top=False, show_base=False,
   #                 cmap='plasma')
   # viewer.show()

Advanced 2D visualization
^^^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/view_2d_advanced.py``

.. code-block:: python

   """
   Example: Using Viewer2D with multiple horizons and custom styling
   
   This example demonstrates advanced usage of the 2D matplotlib viewer:
   - Adding multiple horizons to the same plot
   - Customizing themes and appearance
   - Using different visualization options
   """
   
   from petres.models import Horizon
   from petres.interpolators import IDWInterpolator
   from petres.viewers import Viewer2D, Viewer2DTheme
   import numpy as np
   
   # Create sample horizons
   xy1 = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
   z1 = np.array([100, 105, 110, 102, 106])
   horizon1 = Horizon(name="Horizon 1", interpolator=IDWInterpolator(), xy=xy1, z=z1)
   
   xy2 = np.array([[10, 10], [90, 10], [90, 90], [10, 90], [50, 50]])
   z2 = np.array([120, 125, 130, 122, 126])
   horizon2 = Horizon(name="Horizon 2", interpolator=IDWInterpolator(), xy=xy2, z=z2)
   
   # Example 1: Simple horizon view
   print("Example 1: Simple horizon view")
   horizon1.show2d(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50)
   
   # Example 2: Custom theme
   print("Example 2: Custom theme with different colormap")
   theme = Viewer2DTheme(
       figure_size=(12, 10),
       background="lightgray",
       grid=True,
       grid_alpha=0.5,
       xlabel="Easting (m)",
       ylabel="Northing (m)",
       title="Custom Styled Horizon Map",
       colormap="plasma",
       aspect="equal"
   )
   
   viewer = Viewer2D(theme=theme)
   viewer.add_horizon(
       horizon1, 
       xlim=(0, 100), 
       ylim=(0, 100), 
       ni=60, 
       nj=60,
       show_contours=True,
       contour_levels=15
   )
   viewer.show()
   
   # Example 3: Multiple horizons (would need subplots or separate plots)
   print("Example 3: Horizon with custom contour levels")
   horizon2.show2d(
       xlim=(0, 100), 
       ylim=(0, 100), 
       ni=50, 
       nj=50,
       cmap="terrain",
       contour_levels=20
   )
   
   print("All examples complete!")
