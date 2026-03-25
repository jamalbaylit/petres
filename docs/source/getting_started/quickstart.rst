Quickstart
==========

This guide shows the shortest path to a first working Petres workflow.

In a few steps, you will:

- create a simple grid
- inspect its shape
- visualize it
- attach a property

Overview
--------

Petres is designed for reservoir modeling workflows centered around:

- geological surfaces and zones
- corner-point and structured grid representations
- property modeling
- visualization
- simulator-oriented data structures

The example below keeps the workflow intentionally small so you can get a working result immediately.

Create a simple grid
--------------------

Start by creating a basic rectilinear grid:

.. code-block:: python

   from petres.grid import CornerPointGrid

   grid = CornerPointGrid.from_rectilinear(
       x=[0.0, 500.0, 1000.0],
       y=[0.0, 500.0, 1000.0],
       z=[0.0, 50.0, 100.0],
   )

   print(grid.shape)

This creates a grid with:

- 2 cells in the x direction
- 2 cells in the y direction
- 2 layers in the z direction

Depending on your API, ``grid.shape`` typically follows the simulator-oriented cell layout.

Visualize the grid
------------------

If your visualization backend is installed, display the grid:

.. code-block:: python

   grid.show()

For many users, this is the first useful checkpoint: confirming that the geometry was created correctly.

Assign a simple property
------------------------

A common next step is to attach a cell-based property such as porosity.

For example:

.. code-block:: python

   import numpy as np

   poro = np.full(grid.shape, 0.22, dtype=float)

   grid.properties.create(
       "poro",
       values=poro,
       description="Porosity",
       eclipse_keyword="PORO",
   )

   print(grid.properties["poro"].mean)

This creates a uniform porosity field across all cells.

Visualize a property
--------------------

Once a property exists, you can visualize it on the grid:

.. code-block:: python

   grid.show(scalars="poro")

If your viewer accepts property arrays directly, your workflow may also support:

.. code-block:: python

   grid.show(scalars=grid.properties["poro"].values)

Use the option that matches your public API.

Minimal end-to-end example
--------------------------

The following example combines grid creation, property assignment, and visualization in one place:

.. code-block:: python

   import numpy as np
   from petres.grid import CornerPointGrid

   grid = CornerPointGrid.from_rectilinear(
       x=[0.0, 500.0, 1000.0],
       y=[0.0, 500.0, 1000.0],
       z=[0.0, 50.0, 100.0],
   )

   poro = np.full(grid.shape, 0.22, dtype=float)

   grid.properties.create(
       "poro",
       values=poro,
       description="Porosity",
       eclipse_keyword="PORO",
   )

   print("Grid shape:", grid.shape)
   print("Porosity mean:", grid.properties["poro"].mean)

   grid.show(scalars="poro")

What to learn next
------------------

After this quickstart, the most natural next topics are:

- creating more realistic corner-point grids
- working with horizons and zones
- building and populating grid properties
- importing or exporting simulator-oriented formats

Recommended next pages:

- :doc:`first_grid`
- :doc:`/tutorials/index`
- :doc:`/concepts/index`

Notes
-----

The exact import paths and method signatures may vary slightly depending on your public API design. The examples in this guide assume a user-facing API centered around:

- ``CornerPointGrid``
- ``grid.properties.create(...)``
- ``grid.show(...)``

If your current implementation differs, keep the structure of this page but align the code snippets with your final public API.

Common issues
-------------

``ModuleNotFoundError: No module named 'petres'``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Petres is not installed in the active Python environment. Return to :doc:`installation` and confirm that your environment is activated before installing.

Visualization does not open
^^^^^^^^^^^^^^^^^^^^^^^^^^^

This usually means that the required visualization dependencies are not installed or the current environment does not support rendering. Confirm that your visualization backend is available and working.

Next step
---------

Continue to :doc:`first_grid` for a slightly more detailed walkthrough of grid creation and inspection.