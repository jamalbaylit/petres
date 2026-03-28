Exporting Grid Models
=====================

Overview
--------

Currently, Petres supports exporting grids to the Eclipse ``.GRDECL`` file format,
which is especially used for :ref:`Corner-Point grids <corner-point-grids>`.

Exporting a grid to ``.GRDECL`` file typically includes:

- Grid geometry (``SPECGRID``, ``COORD``, ``ZCORN``)
- Active cell mask (``ACTNUM``)
- Optional grid properties (e.g., ``PORO``, ``PERMX``)

.. note::
    For a comprehensive understanding of the underlying keywords, refer to the :ref:`Corner-Point Grid Representation in ECLIPSE <corner-point-grid-representation-in-eclipse>` section.

Exporting Grid Geometry
-----------------------

:class:`~petres.grids.cornerpoint.CornerPointGrid` can be exported directly to a ``.GRDECL`` file:

.. code-block:: python

   grid.to_grdecl("model.grdecl")

.. note::
   The exported GRDECL file can be incorporated into an Eclipse simulation
   by including it within the ``GRID`` section of the simulation DATA file using the
   ``INCLUDE`` keyword:

   .. code-block:: text

      GRID

      INCLUDE
      'path/to/example.grdecl' /

   The GRDECL file contains the grid definition (e.g., ``COORD``, ``ZCORN``,
   ``ACTNUM``) and typically includes a ``SPECGRID`` keyword. However,
   ``SPECGRID`` is used only for internal consistency checks and does not
   replace the required grid declaration in the ``RUNSPEC`` section.

   Therefore, the grid dimensions must be explicitly defined using the
   ``DIMENS`` keyword in ``RUNSPEC`` section:

   .. code-block:: text

      RUNSPEC

      DIMENS
      Ni Nj Nk /

   where ``Ni``, ``Nj``, and ``Nk`` denote the number of grid cells in the
   i, j, and k directions, respectively. These values must be consistent
   with the dimensions of the exported grid.

Exporting Grid Properties
-------------------------

Grid properties can be exported together with the geometry:

.. code-block:: python

   grid.to_grdecl(
       "model.grdecl",
       properties=["poro", "perm"]
   )

Each property is written using its associated simulator keyword
(e.g., ``PORO``, ``PERMX``).

Notes:

- Property arrays must match the grid shape ``(nk, nj, ni)``
- Property names should correspond to registered grid properties


Handling Active Cells (ACTNUM)
------------------------------

Petres grids support inactive cells through a boolean mask.

During export, this mask is written as the ``ACTNUM`` keyword:

- ``1`` → active cell
- ``0`` → inactive cell

Example:

.. code-block:: python

   grid.to_grdecl(
       "model.grdecl",
       include_inactive=True
   )

If inactive cells are excluded, only active cells are considered in
downstream workflows depending on simulator behavior.


File Structure
--------------

A typical exported GRDECL file contains:

- ``SPECGRID`` — grid dimensions
- ``COORD`` — pillar geometry
- ``ZCORN`` — corner depths
- ``ACTNUM`` — active cell mask (optional)
- Property keywords (e.g., ``PORO``, ``PERMX``)

These keywords follow the standard Eclipse format and are compatible
with most corner-point grid simulators.


Common Pitfalls
---------------

**Mismatched Property Dimensions**

Ensure that property arrays match the grid shape exactly:

- Expected shape: ``(nk, nj, ni)``


**Incorrect Depth Convention**

Most simulators expect depth to be **positive downward**.


**Coordinate Orientation**

Grid orientation must follow a consistent coordinate system.
Incorrect orientation may lead to flipped geometries in simulators.


**Inactive Cell Handling**

Be explicit about whether inactive cells should be included during export.


Next Steps
----------

After exporting the grid, typical next steps include:

- Importing the model into a simulator (e.g., Eclipse or Petrel)
- Defining well controls and schedules
- Running flow simulations

For further details on grid construction and property modeling, see:

- :doc:`grid-modeling-from-horizons-and-zones`
- :doc:`grid-properties`
- :doc:`../api/index`