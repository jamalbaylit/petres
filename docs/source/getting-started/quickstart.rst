Quickstart
==========

Create a Simple Grid
--------------------

Create a basic :ref:`Rectilinear grid <rectilinear-grids>` using the
:ref:`Corner-Point grid <corner-point-grids>` representation:

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_rectilinear(
      x=[0, 500, 700, 1000],
      y=[0, 500, 800],
      z=[0, 30, 100],
   )

   # Print a summary of the grid
   print(grid.summary())

This defines a grid consisting of 3 cells in the x-direction, 2 cells in the y-direction, and 2 layers in the z-direction.


Visualize the Grid
------------------

Render the grid in an interactive 3D viewer:

.. code-block:: python

   grid.show(scalars="depth")


Assign a Property Distribution
------------------------------

Properties are defined per cell and attached to the grid. Create a porosity property:

.. code-block:: python

   poro = grid.properties.create(
      name="porosity",
      description="Porosity",
      eclipse_keyword="PORO",
   )

The ``eclipse_keyword`` argument is optional, but enables direct export
to Eclipse-compatible format.

Assign values using a lognormal distribution:

.. code-block:: python

   poro.fill_lognormal(
      mean=0.24,
      std=0.03,
      min=0.0,
      max=0.35,
   )


Visualize the Property
----------------------

Display the property directly:

.. code-block:: python

   poro.show()

Or alternatively through the grid using the property name:

.. code-block:: python

   grid.show(scalars="porosity")


Export to Eclipse Format
------------------------

Export the grid and its associated properties in Eclipse
``.GRDECL`` format:

.. code-block:: python

   grid.to_grdecl("example.grdecl", properties=["porosity"])


What to Learn Next
------------------

After this quickstart, continue with the
next tutorials:

- Build geological surfaces from data picks: :doc:`/tutorials/horizon-modeling`
   
- Turn surfaces into stratigraphic intervals and layering: :doc:`/tutorials/zone-modeling`

- Assemble a full structural grid from zones and pillars: :doc:`/tutorials/grid-modeling-from-horizons-and-zones`

- Model reservoir properties: :doc:`/tutorials/property-modeling`
