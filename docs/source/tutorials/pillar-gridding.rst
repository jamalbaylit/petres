Pillar Gridding
===============

:ref:`Corner-Point grids <corner-point-grids>` rely on
pillars as their fundamental structural framework. 
In Petres, pillars are modeled separately, similar to 
how Petrel handles them, allowing for precise control 
over the geometry of the grid independent of the cells themselves.
If you are unfamiliar with pillars, see the :ref:`pillar-geometry` section for an introduction.

Creating a Pillar Grid
----------------------

Pillar grids can currently be created in two ways. 
Regular pillar grids are defined with uniform spacing, 
while rectilinear pillar grids are defined from 
explicitly provided coordinate arrays.

.. note::

    At this stage, Petres supports only **vertical pillars**. Skewed or
    faulted pillar geometries are not yet supported.


Regular Pillar Grids
~~~~~~~~~~~~~~~~~~~~

A regular pillar grid is defined by specifying the model extent in the
``x`` and ``y`` directions together with the number of cells along each axis.
This is conceptually similar to creating a regular grid (see :ref:`creating-regular-grid`).

.. code-block:: python

    from petres.grids import PillarGrid

    pillars = PillarGrid.from_regular(
        xlim=(0, 100),
        ylim=(0, 100),
        ni=50,
        nj=50,
    )

Here, ``xlim`` and ``ylim`` define the spatial extent of the model in the
x and y directions, respectively, while ``ni`` and ``nj`` control the
number of cells along each axis.

Alternatively, it can be defined using cell sizes instead of
cell counts.

.. code-block:: python

    pillars = PillarGrid.from_regular(
        xlim=(0, 100),
        ylim=(0, 100),
        dx=2,
        dy=2,
    )

Here, ``dx=2`` and ``dy=2`` specify the cell size in the x and y directions, respectively.


Rectilinear Pillar Grids
~~~~~~~~~~~~~~~~~~~~~~~~

A rectilinear pillar grid allows **non-uniform spacing** along each axis,
making it suitable for local refinement in specific regions of the model.
This follows the same principles as rectilinear grid generation (see :ref:`creating-rectilinear-grid`).

.. code-block:: python

    pillars = PillarGrid.from_rectilinear(
        x=[0, 10, 50, 70, 100],
        y=np.linspace(0, 100, 50),
    )

In this example, the ``x`` coordinates are defined explicitly, resulting
in non-uniform spacing, while the ``y`` coordinates are generated using
:meth:`numpy.linspace`, producing evenly spaced values.

Specifying Top and Base Depths
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pillar top and base values can be defined explicitly when creating a
rectilinear grid, allowing precise placement of the pillar geometry
within the model.

.. code-block:: python

    pillars = PillarGrid.from_rectilinear(
        x=[0, 10, 50, 70, 100],
        y=np.linspace(0, 100, 50),
        top=1000,
        base=1500,
    )

In this example, the pillars are positioned with tops at ``1000`` and
bases at ``1500``. These values may represent either elevation or depth,
depending on the conventions used in your workflow.

.. note::

    By default, ``top=0.0`` and ``base=1.0``. If you are concerned
    about numerical precision or want to adjust the vertical scale of your
    grid, you can modify these values when creating the pillar grid.

Visualize the Pillar Grid
-------------------------

The grid can be visualized interactively using the :meth:`show` method.

.. code-block:: python

    pillars.show()

This provides a quick way to inspect the geometry of the generated pillar
grid.


Next Steps
----------

- :doc:`grid-modeling-from-horizons-and-zones`