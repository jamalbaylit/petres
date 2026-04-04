Importing Grid Models
=====================

Currently, Petres supports importing grids only from Eclipse ``.GRDECL`` files, with a limited set of supported keywords.
Importing allows you to load grid geometry, grid properties, and the active cell mask into a :class:`~petres.grids.CornerPointGrid` object.

.. note::

   For a detailed description of the keywords used in ``.GRDECL`` files and their structure, see the :ref:`Corner-Point Grid Representation in Eclipse <corner-point-grid-representation-in-eclipse>` section.

Importing Grid Geometry
-----------------------

A grid can be imported directly from a ``.GRDECL`` file using the :meth:`~petres.grids.CornerPointGrid.from_grdecl` method:

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_grdecl("model.grdecl")
   grid.show()

By default, this method automatically reads:

- Grid geometry (``COORD``, ``ZCORN``, ``SPECGRID``, or ``DIMENS``)
- Active cell mask (``ACTNUM``)

.. important::

   The file must contain at least the grid geometry keywords (``COORD``, ``ZCORN``, ``SPECGRID``, or ``DIMENS``).

To import the grid without the active cell mask, set the ``use_actnum`` parameter to ``False``:

.. code-block:: python

   grid = CornerPointGrid.from_grdecl("model.grdecl", use_actnum=False)

This is useful when you want to define ``ACTNUM`` manually after import.

Importing Properties
--------------------

Properties stored in the Eclipse file can be imported by specifying their keywords in the ``properties`` argument:

.. code-block:: python

   grid = CornerPointGrid.from_grdecl(
      "model_with_props.grdecl",
      properties=["PORO", "PERMX"],
   )
   porosity = grid.properties["PORO"]
   permeability = grid.properties["PERMX"]

Only the specified properties are imported.