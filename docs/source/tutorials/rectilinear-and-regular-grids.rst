Rectilinear and Regular Grids
=============================

In this tutorial, you will learn how to create :ref:`Rectilinear <rectilinear-grids>` and :ref:`Regular <regular-grids>` grids in Petres.


.. _creating-rectilinear-grid:

Creating a Rectilinear Grid
---------------------------

A **Rectilinear grid** is defined by specifying grid line coordinates along
each axis. The spacing between grid lines can vary independently in each
direction.

.. code-block:: python

   from petres.grids import CornerPointGrid

   x = [0, 50, 100, 200, 400, 700, 1000]
   y = [0, 100, 300, 600, 1000]
   z = [0, 10, 25, 50, 80, 100]

   grid = CornerPointGrid.from_rectilinear(x=x, y=y, z=z)
   grid.show()


The arrays ``x``, ``y``, and ``z`` define grid lines, 
so the number of cells is ``len(x)-1``, ``len(y)-1``, and ``len(z)-1``.

.. note::
   
   Internally, Petres converts this into a Corner-Point grid.



.. _creating-regular-grid:

Creating a Regular Grid
-----------------------

In Petres, a :ref:`Regular grid <regular-grids>` can be defined in two equivalent ways:

- By specifying the **number of cells**
- By specifying the **cell sizes**

Using Number of Cells
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_regular(
      xlim=(0, 1000),
      ylim=(0, 1000),
      zlim=(0, 100),
      ni=20,
      nj=20,
      nk=3
   )

   print(grid.summary())

   grid.show()

The domain limits are defined by ``xlim``, ``ylim``, and ``zlim``,
each specified as a tuple of ``(min, max)``, which define the spatial extent
of the grid. The cell sizes are controlled by ``dx``, ``dy``, and ``dz``
arguments in each direction. 
The :meth:`summary` method provides a brief overview of the grid, 
while :meth:`show` visualizes it.

.. note::
   For more advanced visualization options refer to :doc:`grid-visualization`.

Using Cell Sizes
~~~~~~~~~~~~~~~~

Alternatively, the grid can be defined by specifying the size of cells.

.. code-block:: python

   grid = CornerPointGrid.from_regular(
      xlim=(0, 1000),
      ylim=(0, 1000),
      zlim=(0, 100),
      dx=20,
      dy=20,
      dz=33.333333333333336
   )

Here, ``dx``, ``dy``, and ``dz`` control the cell size in each direction.


Next Steps
----------

- :doc:`property-modeling`
- :doc:`exporting-grid`
