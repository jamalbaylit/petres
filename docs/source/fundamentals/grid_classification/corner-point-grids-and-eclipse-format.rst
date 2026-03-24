Corner-Point Grid
=================

Definition
----------

A **Corner-Point Grid** is a three-dimensional structured grid used in reservoir modeling.

- Uses logical indexing: ``(i, j, k)``
- Geometry is independent from topology

.. figure:: _static/images/cpg_example.png
   :align: center
   :width: 70%

   Figure 1: Example non-conforming corner-point grid (4×2×3 cells).

Cell Representation
-------------------

Each cell:

- Has 8 corners
- Forms a hexahedral shape

Corner coordinates are not stored independently.

Instead, geometry is split into:

- Pillars
- Corner depth values

Pillar Geometry
---------------

A pillar is defined by:

- Top point: ``(x_top, y_top, z_top)``
- Bottom point: ``(x_bot, y_bot, z_bot)``

Pillars define the structural skeleton of the grid.

.. figure:: _static/images/pillar_indexing.png
   :align: center
   :width: 60%

   Figure 2: Pillar indexing for cell (i, j, k).

Corner Interpolation
--------------------

Corner position is computed using linear interpolation:

- Interpolation parameter:

  ``t = (z_c - z_top) / (z_bot - z_top)``

- Coordinates:

  ``x_c = x_top + t (x_bot - x_top)``
  ``y_c = y_top + t (y_bot - y_top)``

Eclipse Grid Representation
---------------------------

Corner-point grids in Eclipse are defined using:

- ``DIMENS`` → Grid size
- ``COORD`` → Pillar geometry
- ``ZCORN`` → Corner depths
- ``ACTNUM`` → Active cells

COORD
-----

Stores pillar endpoints:

- Shape: ``[Nj+1, Ni+1, 6]``
- Size: ``6(Ni+1)(Nj+1)``

ZCORN
-----

Stores depth of each corner:

- Shape: ``[2Nk, 2Nj, 2Ni]``
- Size: ``8NiNjNk``

.. figure:: _static/images/zcorn_indexing.png
   :align: center
   :width: 70%

   Figure 3: ZCORN indexing for cell corners.

ACTNUM
------

Defines active cells:

- ``1`` → active
- ``0`` → inactive

ACTNUM acts as a mask and does not affect geometry.