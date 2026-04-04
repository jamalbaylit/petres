Exporting Grid Models
=====================

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

:class:`~petres.grids.CornerPointGrid` can be exported directly to a ``.GRDECL`` file:

.. code-block:: python

   grid.to_grdecl("model.grdecl")

By default, the active cell mask ``ACTNUM`` is included in the export. To exclude it:

.. code-block:: python

   grid.to_grdecl("example_grid.grdecl", include_actnum=False)

This is useful when you prefer to manage
the active cell definition separately in your simulation setup.

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

   # Create a porosity property
   poro = grid.properties.create(
      name="porosity",
      description="Porosity",
      eclipse_keyword="PORO",
   )
   poro.fill(0.2)
   
   # Export grid with selected properties
   grid.to_grdecl(
      "model.grdecl",
      properties=["porosity"]
   )

.. important::
   If the ``properties`` argument is not defined in :meth:`to_grdecl`, **all existing properties** will be exported by default.

Each property is written using its associated simulator keyword defined during property creation
(e.g., ``PORO``, ``PERMX``).


It is also possible to export a property without the grid geometry:

.. code-block:: python

   poro.to_grdecl("porosity.grdecl")

.. note::
   In order to export a property, the ``eclipse_keyword`` variable **must** be filled when creating the property.
