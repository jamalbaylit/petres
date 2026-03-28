Exporting Grid Models
=====================

Overview
--------

Petres grids can be exported to simulator-compatible formats for use in
reservoir simulation workflows.

The primary supported format is the **Eclipse-style GRDECL** format, which
is widely used in:

- Eclipse
- Petrel
- Other corner-point grid based simulators

Exporting a grid typically includes:

- Grid geometry (``SPECGRID``, ``COORD``, ``ZCORN``)
- Active cell mask (``ACTNUM``)
- Optional grid properties (e.g., ``PORO``, ``PERMX``)

.. seealso::

   - :doc:`corner-point-grid-creation`
   - :doc:`grid-modeling-from-horizons-and-zones`
   - :doc:`grid-properties`


Exporting Grid Geometry
----------------------

A corner-point grid can be exported directly to a GRDECL file:

.. code-block:: python

   grid.to_grdecl("model.grdecl")

This writes the core grid definition including:

- ``SPECGRID``: grid dimensions
- ``COORD``: pillar coordinates
- ``ZCORN``: cell corner depths


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

---

**Incorrect Depth Convention**

Most simulators expect depth to be **positive downward**.

---

**Coordinate Orientation**

Grid orientation must follow a consistent coordinate system.
Incorrect orientation may lead to flipped geometries in simulators.

---

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