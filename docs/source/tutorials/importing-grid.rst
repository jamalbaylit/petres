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

Interactive Example (Norne)
---------------------------

This page can also include a browser-based interactive 3D rendering exported as HTML.
Two variants are generated from the Norne grid in ``examples/data/corner_point/Norne.GRDECL``:
one optimized for light docs theme and one for dark docs theme.

To regenerate the interactive HTML:

.. code-block:: bash

   python docs/scripts/generate_importing_grid_interactive.py

.. raw:: html

    <div class="petres-interactive-viewer" id="petres-importing-grid-viewer">
       <iframe
          id="petres-importing-grid-viewer-light"
          src="../_static/tutorials/importing-grid-norne-interactive-light.html"
          loading="lazy"
          title="Interactive Norne grid viewer (light theme)">
       </iframe>
       <iframe
          id="petres-importing-grid-viewer-dark"
          src="../_static/tutorials/importing-grid-norne-interactive-dark.html"
          loading="lazy"
          title="Interactive Norne grid viewer (dark theme)">
       </iframe>
    </div>

    <script>
       (function () {
          const root = document.documentElement;
          const body = document.body;
          const lightFrame = document.getElementById("petres-importing-grid-viewer-light");
          const darkFrame = document.getElementById("petres-importing-grid-viewer-dark");
          if (!lightFrame || !darkFrame) {
             return;
          }

          const prefersDark = () => {
             return !!(window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches);
          };

          const updateViewerTheme = () => {
             const bodyTheme = body ? (body.getAttribute("data-theme") || "") : "";
             const htmlTheme = root.getAttribute("data-theme") || "";
             const dataTheme = (bodyTheme || htmlTheme).toLowerCase();
             const classTheme = root.className || "";
             const isDark =
                dataTheme === "dark" ||
                (dataTheme === "auto" && prefersDark()) ||
                classTheme.toLowerCase().includes("theme-dark") ||
                (!dataTheme && prefersDark());

             lightFrame.hidden = isDark;
             darkFrame.hidden = !isDark;
          };

          updateViewerTheme();

          if (window.matchMedia) {
             const mq = window.matchMedia("(prefers-color-scheme: dark)");
             if (mq.addEventListener) {
                mq.addEventListener("change", updateViewerTheme);
             } else if (mq.addListener) {
                mq.addListener(updateViewerTheme);
             }
          }

          const observer = new MutationObserver(updateViewerTheme);
          observer.observe(root, {
             attributes: true,
             attributeFilter: ["data-theme", "class"],
          });
          if (body) {
             observer.observe(body, {
                attributes: true,
                attributeFilter: ["data-theme", "class"],
             });
          }
       })();
    </script>

.. note::

   If your browser blocks local iframe content when previewing docs directly from files,
   run Sphinx and open the served HTML output instead.

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