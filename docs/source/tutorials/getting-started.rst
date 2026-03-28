Getting Started
===============

Petres follows a simple workflow: define a grid, attach properties, and
export the model for simulation.


Your First Grid
---------------

Create a regular grid:

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_regular(
      xlim=(0, 1000),
      ylim=(0, 1000),
      zlim=(0, 100),
      ni=20,
      nj=20,
      nk=3,
   )

   # Print a summary of the grid
   print(grid.summary())

This defines a grid with :math:`3 \times 2 \times 2` cells in the x, y, and z directions.


Visualize the Grid
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   grid.show()

The grid is rendered as a corner-point geometry derived from pillar
interpolation.


Add a Property
--------------

Attach a porosity field to the grid:

.. code-block:: python

   porosity = grid.properties.create(
      name="porosity",
      description="Porosity",
   )

Assign a uniform value:

.. code-block:: python

   porosity.fill(0.2)

Properties are stored per cell with shape ``(nk, nj, ni)``.


Visualize the Property
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   porosity.show()

Or equivalently:

.. code-block:: python

   grid.show(scalars="porosity")

Both methods map cell values to colors on the grid.


Export to Eclipse
-----------------

Export the grid and attached properties to GRDECL format:

.. code-block:: python

   grid.to_grdecl("example.grdecl")

