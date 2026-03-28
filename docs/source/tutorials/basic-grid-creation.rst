Basic Grids
===========

In this tutorial, you will learn how to create simple structured grids in Petres.

We will cover:

- Rectilinear grids (non-uniform spacing)
- Regular grids (uniform spacing)

These are the simplest ways to define a grid and are typically used as the
starting point for more advanced modeling workflows.


Rectilinear Grids
-----------------

A **rectilinear grid** is defined by specifying grid line coordinates along
each axis. The spacing between grid lines can vary independently in each
direction.

Create a Rectilinear Grid
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from petres.grids.cornerpoint import CornerPointGrid

   x = [0, 50, 100, 200, 400, 700, 1000]
   y = [0, 100, 300, 600, 1000]
   z = [0, 10, 25, 50, 80, 100]

   grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)
   grid.show()


Explanation
~~~~~~~~~~~

The arrays ``x``, ``y``, and ``z`` define the grid lines along each axis.

- Number of cells in x-direction → ``len(x) - 1``
- Number of cells in y-direction → ``len(y) - 1``
- Number of layers in z-direction → ``len(z) - 1``

Because the spacing is not uniform, cell sizes vary across the domain. This
allows local refinement where needed, for example:

- smaller cells near wells  
- larger cells in far-field regions  

Internally, Petres converts this into a Corner-Point grid using vertical pillars.



Regular Grids
-------------

A **regular grid** is a special case of a rectilinear grid where spacing is
uniform along each axis.

Create a Regular Grid (by Cell Counts)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

   print(grid.summary())

   grid.show(scalars="active")


Explanation
~~~~~~~~~~~

Instead of specifying grid lines explicitly, you define:

- domain limits → ``xlim``, ``ylim``, ``zlim``
- number of cells → ``ni``, ``nj``, ``nk``

Petres automatically generates evenly spaced grid lines.

The ``summary()`` method provides a quick overview of the grid dimensions and
properties.

The ``scalars="active"`` option visualizes active cells in the grid.



Regular Grid Using Cell Sizes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can define a regular grid using cell sizes instead of the
number of cells.

.. code-block:: python

   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       dx=20,
       dy=20,
       dz=33.333333333333336,
   )

   grid.show()


Explanation
~~~~~~~~~~~

Here, the grid resolution is controlled directly by:

- ``dx`` → cell size in x-direction  
- ``dy`` → cell size in y-direction  
- ``dz`` → layer thickness  

The number of cells is inferred from the domain size and spacing.

This approach is often more intuitive when you know the desired resolution
rather than the total number of cells.



Rectilinear vs Regular
----------------------

A regular grid is simply a constrained form of a rectilinear grid:

- **Rectilinear** → spacing can vary  
- **Regular** → spacing is constant  

In practice:

- use **regular grids** for simple models and quick setups  
- use **rectilinear grids** when local refinement is required  

