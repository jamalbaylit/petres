Property Modeling
=================

Examples for assigning and manipulating properties on grids.

Edit Grid Property
^^^^^^^^^^^^^^^^^^

Import a grid with properties, visualize property distributions, and apply
simple transformations.

.. code-block:: python

   """Import and manipulate a corner-point grid property from a ".GRDECL" file."""
   
   from petres.grids import CornerPointGrid
   
   # Load grid from remote ".GRDECL" file
   path = "https://raw.githubusercontent.com/jamalbaylit/petres/v0.1.0/data/opm/norne/grdecl/norne_with_props.grdecl"
   
   grid = CornerPointGrid.from_grdecl(path, properties=["PORO"])
   
   # Visualize depth
   grid.show(scalars="depth", z_scale=5)
   
   # Access porosity property
   porosity = grid.properties["PORO"]
   
   # Visualize original porosity
   porosity.show(z_scale=5)
   
   # Convert porosity to percentage
   porosity_pct = porosity.apply(lambda x: x * 100, source="PORO")
   porosity_pct.show(z_scale=5)
   
   # Scale porosity values
   porosity_scaled = porosity.apply(lambda x: x / 2, source="PORO")
   porosity_scaled.show(z_scale=5)
   
   # Export grid
   grid.to_grdecl("grid.grdecl")
