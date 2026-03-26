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

   # Inspect grid dimensions
   print(grid.shape)

This defines a grid with:

- 3 cells in the x-direction
- 2 cells in the y-direction
- 2 layers in the z-direction


Visualize the Grid
------------------

Render the grid in an interactive 3D viewer:

.. code-block:: python

   grid.show()


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
-----------------------

Export the grid and its associated properties in Eclipse-compatible
``.GRDECL`` format:

.. code-block:: python

   grid.to_grdecl("example.grdecl", properties=["porosity"])


What to Learn Next
------------------

After this quickstart, consider exploring:

- Building corner-point grids from geological surfaces
- Defining horizons and zones for stratigraphic modeling
- Advanced property modeling and spatial distributions
- Importing existing GRDECL files 