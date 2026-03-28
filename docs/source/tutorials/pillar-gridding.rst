Pillar Grid Creation
====================

This tutorial demonstrates several ways to construct a ``PillarGrid`` in
Petres. Pillar grids define the structural framework of corner-point
grids and are commonly used as the geometric basis for more advanced
grid modeling workflows.

In this tutorial, you will learn how to:

- create a regular pillar grid from domain limits and cell counts,
- create a regular pillar grid from cell spacing,
- build a rectilinear pillar grid with non-uniform coordinates,
- use ``numpy`` to generate coordinate arrays,
- manually define pillar top and bottom depths, and
- visualize the resulting grid.

Import Modules
--------------

To get started with pillar gridding, you need to import the necessary modules: 

.. code-block:: python

   from petres.grids import PillarGrid
   import numpy as np

Ensure that you have NumPy installed as well.

Create a Regular Pillar Grid from Domain Limits
-----------------------------------------------

A regular pillar grid can be created by defining the extent of the model
in the ``x`` and ``y`` directions together with the number of cells
along each axis.

.. code-block:: python

   pillars = PillarGrid.from_regular(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )

Here:

- ``xlim=(0, 100)`` defines the model extent in the x-direction,
- ``ylim=(0, 100)`` defines the model extent in the y-direction,
- ``ni=50`` specifies the number of cells along x, and
- ``nj=50`` specifies the number of cells along y.

This creates a regular grid with uniform spacing in both horizontal
directions.


Create a Regular Pillar Grid from Cell Spacing
----------------------------------------------

Instead of specifying the number of cells directly, you can define the
grid using cell spacing.

.. code-block:: python

   pillars = PillarGrid.from_regular(
       xlim=(0, 100),
       ylim=(0, 100),
       dx=2,
       dy=2,
   )

In this case:

- ``dx=2`` sets the cell size in the x-direction, and
- ``dy=2`` sets the cell size in the y-direction.

This is often convenient when the desired grid resolution is known in
advance.


Create a Rectilinear Pillar Grid
--------------------------------

A rectilinear grid allows non-uniform spacing along each axis. This is
useful when local refinement is needed in selected regions of the model.

.. code-block:: python

   pillars = PillarGrid.from_rectilinear(
       x=[0, 10, 50, 70, 100],
       y=np.linspace(0, 100, 50),
   )

In this example:

- the ``x`` coordinates are defined explicitly, resulting in non-uniform
  spacing in the x-direction,
- the ``y`` coordinates are generated using ``numpy.linspace``, producing
  evenly spaced coordinates in the y-direction.

This approach is useful when grid spacing needs to vary while preserving
a structured pillar layout.


Use NumPy to Generate Coordinates
---------------------------------

You can also use ``numpy`` arrays directly to define the grid geometry.

.. code-block:: python

   pillars = PillarGrid.from_rectilinear(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       z_top=0,
       z_bottom=15,
   )

Here, both ``x`` and ``y`` are generated using ``numpy.linspace``.
Additionally:

- ``z_top=0`` defines the elevation or depth of the pillar tops,
- ``z_bottom=15`` defines the elevation or depth of the pillar bottoms.

This creates a structured pillar grid with uniform horizontal spacing and
constant vertical pillar endpoints.


Specify Pillar Top and Bottom Depths Manually
---------------------------------------------

You may also define the top and bottom elevations or depths explicitly
when creating a rectilinear grid.

.. code-block:: python

   pillars = PillarGrid.from_rectilinear(
       x=[0, 10, 50, 70, 100],
       y=np.linspace(0, 100, 50),
       z_top=1000,
       z_bottom=1500,
   )

This is useful when the pillar grid needs to be placed at a specific
depth interval within the model.

In this example:

- the pillar tops are placed at ``1000``,
- the pillar bottoms are placed at ``1500``.

The values may represent elevation or depth, depending on the
conventions used in your workflow.


Visualize the Pillar Grid
-------------------------

The grid can be visualized interactively using the ``show`` method.

.. code-block:: python

   pillars.show()

This provides a quick way to inspect the geometry of the generated pillar
grid.


Complete Example
----------------

The full example is shown below.

.. code-block:: python

   from petres.grids import PillarGrid
   import numpy as np

   pillars = PillarGrid.from_regular(xlim=(0, 100), ylim=(0, 100), ni=50, nj=50)
   pillars = PillarGrid.from_regular(xlim=(0, 100), ylim=(0, 100), dx=2, dy=2)

   pillars = PillarGrid.from_rectilinear(
       x=[0, 10, 50, 70, 100],
       y=np.linspace(0, 100, 50),
   )

   # You can also use NumPy to generate the coordinates.
   pillars = PillarGrid.from_rectilinear(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       z_top=0,
       z_bottom=15,
   )

   # You may also specify the pillar top and bottom depths manually.
   pillars = PillarGrid.from_rectilinear(
       x=[0, 10, 50, 70, 100],
       y=np.linspace(0, 100, 50),
       z_top=1000,
       z_bottom=1500,
   )

   pillars.show()


Summary
-------

In this tutorial, you learned how to create a ``PillarGrid`` using
different construction methods in Petres. Depending on the modeling
requirements, you can use:

- ``from_regular`` for uniform grids,
- ``from_rectilinear`` for non-uniform structured grids,
- ``numpy`` arrays for flexible coordinate generation, and
- explicit ``z_top`` and ``z_bottom`` values to define pillar geometry
  vertically.

The resulting pillar grid can then serve as a foundation for more
advanced grid construction and modeling workflows.