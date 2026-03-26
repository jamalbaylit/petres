Documentation
==============

Petres uses `Sphinx <https://www.sphinx-doc.org/>`_ with the `Furo <https://pradyunsg.me/furo/>`_ theme to generate comprehensive, professional documentation. This guide covers documentation standards, build processes, and best practices for API reference and tutorials.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Documentation Structure
-----------------------

.. code-block:: text

   docs/
   ├── source/
   │   ├── conf.py                 # Sphinx configuration
   │   ├── index.rst               # Homepage
   │   ├── getting_started/        # Quick-start guides
   │   ├── fundamentals/           # Conceptual docs (grids, zones, etc.)
   │   ├── tutorials/              # Step-by-step examples
   │   ├── api/                    # Auto-generated API reference
   │   ├── developer/              # Development guides (this folder)
   │   ├── _templates/             # Custom Sphinx templates
   │   ├── _static/                # CSS, images, static assets
   │   └── _generated/             # Auto-generated (do not edit)
   └── build/html/                 # Generated HTML output

Building Documentation Locally
------------------------------

**Build HTML documentation:**

.. code-block:: bash

   uv run --group docs sphinx-build -b html docs/source docs/build/html

Output is in ``docs/build/html/index.html``. Open in a browser:

.. tabs::

   .. tab:: macOS / Linux

      .. code-block:: bash

         open docs/build/html/index.html

   .. tab:: Windows (PowerShell)

      .. code-block:: powershell

         Start-Process docs/build/html/index.html

**Live reload during writing** (recommended for iterative work):

.. code-block:: bash

   uv run --group docs sphinx-autobuild docs/source docs/build/html

This watches source files and rebuilds automatically. Browse to ``http://127.0.0.1:8000`` (reload when edits save).

**Build PDF** (requires ``latexmk``, optional):

.. code-block:: bash

   uv run --group docs sphinx-build -b pdf docs/source docs/build/pdf

Docstring Standards
-------------------

All public API docstrings follow **Google style** (`example <https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings>`_). This enables auto-documentation via Sphinx's `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_ and `napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`_ extensions.

Structure
^^^^^^^^^

.. code-block:: python

   def create_cornerpoint_grid(
       rectilinear_vertices: NDArray,
       horizons: Sequence[Horizon],
       zones: Sequence[Zone],
   ) -> CornerPointGrid:
       """Create a corner-point grid from rectilinear vertices, horizons, and zones.

       Builds a structured grid with corner-point (or pillar) geometry,
       allowing complex stratigraphic structures with non-vertical pillars
       and pinched-out zones.

       Args:
           rectilinear_vertices: Mesh grid vertices, shape (nx+1, ny+1, 2).
               Defines the pillar tops in X-Y space.
           horizons: Sequence of Horizon objects defining stratigraphic tops.
           zones: Sequence of Zone objects defining layer names and properties.

       Returns:
           CornerPointGrid: Object with shape (nx, ny, nz) ready for property
               assignment and export to GRDECL or other formats.

       Raises:
           ValueError: If horizons are not strictly ordered (not monotonically increasing in depth).
           ValueError: If zones and horizons counts are inconsistent.

       Examples:
           Create a 50×50×10 grid from a sample dataset:

           .. code-block:: python

               vertices = np.load("vertices.npy")  # Shape (51, 51, 2)
               horizons = [Horizon(...), Horizon(...), ...]
               zones = [Zone("Shale"), Zone("Sand"), ...]
               grid = petres.create_cornerpoint_grid(
                   vertices, horizons, zones
               )
               print(grid.shape)  # (50, 50, 10)

       See Also:
           create_pillar_grid: For axis-aligned rectangular grids.
           Horizon.sample: For interpolating horizon depth at grid locations.
           Zone.divide: For dividing zones into sublayers.

       Note:
           Pillar geometry is inferred from rectilinear vertices. For
           complex non-rectilinear grids, provide custom pillar definitions.
       """
       # Implementation here...

Key Sections:

- **Summary**: One-line description of what the function does
- **Extended description**: 2–3 sentences explaining purpose and behavior
- **Args**: Parameter names, type hints, descriptions. Mark optional with ``optional``
- **Returns**: Return type and description of what it contains
- **Raises**: Exception types and conditions that trigger them
- **Examples**: Runnable code blocks (must be self-contained and correct)
- **See Also**: Related classes/functions for navigation
- **Note** / **Warning**: Important caveats or gotchas

Type Hints
^^^^^^^^^^

Always include type hints in function signatures. Use:

.. code-block:: python

   from typing import Sequence, Optional
   from numpy.typing import NDArray
   import numpy as np

   def interpolate_property(
       grid: CornerPointGrid,
       values: NDArray[np.float64],
       method: str = "idw",
       **kwargs,
   ) -> GridProperty:
       """..."""

**Key types:**

- ``NDArray`` for NumPy arrays with explicit dtype: ``NDArray[np.float64]``
- ``Sequence[T]`` for lists/tuples; ``Optional[T]`` for ``T | None``
- Use ``Literal["option1", "option2"]`` for string enums
- Use ``@overload`` decorator for functions with multiple signatures

Example Types in Docstrings:

.. code-block:: python

   def compute_cell_volumes(grid: CornerPointGrid) -> NDArray[np.float64]:
       """Compute volumes of grid cells.

       Args:
           grid: The structured grid object.

       Returns:
           ndarray of shape (nx, ny, nz) with float64 cell volumes.
       """

Class Documentation
^^^^^^^^^^^^^^^^^^^

Document classes with class-level docstring + attribute docstrings:

.. code-block:: python

   class Horizon:
       """Surfaces representing stratigraphic picks across a region.

       A Horizon is a 2D surface (defined at sample points) that can be
       sampled at arbitrary X-Y coordinates via interpolation. Horizons
       form the boundaries between zones in a corner-point grid.

       Attributes:
           name: Horizon name (e.g., "Top Reservoir", "Base Shale").
           samples: (N, 3) array with X, Y, Z coordinates of pick points.
           interpolator: Interpolator object (IDW, RBF, kriging) for depth prediction.

       Examples:
           Create a horizon from sample picks:

           .. code-block:: python

               samples = np.array([[0, 0, 100], [10, 10, 105], ...])
               horizon = petres.Horizon(
                   name="Top Sand",
                   samples=samples,
                   interpolator=petres.IDWInterpolator(power=2),
               )
       """

Code Examples in Docstrings
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Examples must be:

1. **Correct** — runnable and produce the stated output
2. **Concise** — use realistic but minimal data
3. **Self-contained** — no external file dependencies (use hardcoded arrays if needed)

Good example:

.. code-block:: python

   Examples:
       Create a 5×5×2 grid:

       .. code-block:: python

           import numpy as np
           import petres

           vertices = np.array([[0, 0], [5, 0], [5, 5], [0, 5]])
           grid = petres.create_pillar_grid(vertices, n_layers=2)
           print(grid.shape)  # (5, 5, 2)

Bad example (external dependency):

.. code-block:: python

   Examples:
       # DON'T DO THIS — requires file load
       grid = petres.read_grdecl("../data/field.grdecl")

Namespace and API Exposure
---------------------------

Public APIs must be exposed in module ``__all__``:

.. code-block:: python

   # src/petres/__init__.py
   __all__ = [
       "CornerPointGrid",
       "Horizon",
       "Zone",
       "IDWInterpolator",
       "RBFInterpolator",
       "OrdinaryKrigingInterpolator",
       "UniversalKrigingInterpolator",
       "GridProperty",
       "read_grdecl",
       "write_grdecl",
       # ... other public items
   ]

Only items in ``__all__`` appear in auto-generated API docs and IDE autocomplete.

Building API Reference
----------------------

API reference is auto-generated from docstrings. Files in `docs/source/api/` use `autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_:

.. code-block:: rst

   Core Grid Objects
   ==================

   .. automodule:: petres.grids
      :members:
      :undoc-members:
      :show-inheritance:

This scans ``petres.grids`` module and auto-generates documentation for all public members.

**To regenerate API docs** after code changes:

.. code-block:: bash

   rm -rf docs/source/_generated  # Clear cached generated docs
   uv run --group docs sphinx-build -b html docs/source docs/build/html

Sphinx Configuration
-------------------

Main settings are in `docs/source/conf.py`:

**Extensions enabled:**

- ``sphinx.ext.autodoc`` — auto-generate from docstrings
- ``sphinx.ext.napoleon`` — Google/NumPy docstring parsing
- ``sphinx.ext.intersphinx`` — cross-references to external docs (NumPy, SciPy)
- ``sphinx.ext.mathjax`` — LaTeX math rendering

**Theme (Furo):**

.. code-block:: python

   # conf.py
   html_theme = "furo"
   html_theme_options = {
       "source_file_url": "https://github.com/jamalbaylit/petres/blob/dev/docs/source/{filename}",
       "source_branch": "dev",
   }

**Output:**

- HTML output in ``docs/build/html/``
- LaTeX rendering via MathJax (no local dependencies)

Writing Tutorials and Guides
-----------------------------

Tutorials teach users how to accomplish tasks. Place them in `docs/source/tutorials/`:

**Structure:**

.. code-block:: rst

   Creating a Corner-Point Grid
   ============================

   .. introduction explaining what users will learn

   Prerequisites
   -------------

   Before starting, ensure you have:

   - Installed Petres (see :doc:`../getting_started/installation`)
   - Familiarity with NumPy arrays (see `NumPy docs <https://numpy.org/>`_)

   Step 1: Create Rectilinear Vertices
   -----------------------------------

   A corner-point grid starts with pillar geometry defined by X-Y coordinates.

   .. code-block:: python

       import numpy as np
       import petres

       # Define a 10×10 regular grid
       x = np.linspace(0, 100, 11)  # 11 points → 10 cells
       y = np.linspace(0, 100, 11)
       xx, yy = np.meshgrid(x, y)
       vertices = np.stack([xx, yy], axis=-1)  # Shape (11, 11, 2)

   Step 2: Define Horizons
   -----------------------

   Horizons represent layer boundaries...

Use cross-references to link to API docs:

.. code-block:: rst

   For details on interpolators, see :class:`petres.IDWInterpolator`.
   For grid creation, see :func:`petres.create_cornerpoint_grid`.

Formatting Guidelines
---------------------

**Headings:**

- Use ``=====`` for page titles (top-level)
- Use ``-----`` for sections (level 2)
- Use ``^^^^^`` for subsections (level 3)

**Code blocks:**

.. code-block:: rst

   .. code-block:: python

       import numpy as np
       data = np.array([1, 2, 3])

**Emphasized text:**

.. code-block:: rst

   *italic* for emphasis
   **bold** for strong emphasis
   ``monospace`` for code/symbols

**Math (inline and block):**

.. code-block:: rst

   Inverse distance weighting: :math:`w_i = \frac{1}{d_i^p}`

   Block math:

   .. math::

      w_i = \frac{1}{d_i^p}

**Notes and warnings:**

.. code-block:: rst

   .. note::

      This is important information.

   .. warning::

      Remove this directory with caution!

**Cross-references:**

.. code-block:: rst

   See :doc:`../getting_started/installation` for setup.
   See :ref:`labelname` for anchor link.
   See :class:`CornerPointGrid` for class reference.
   See :func:`create_cornerpoint_grid` for function reference.

Versioning Documentation
------------------------

Documentation builds are versioned with source code:

- **Main branch (`main`)** → production docs at https://petres.readthedocs.io
- **Dev branch (`dev`)** → development docs (if enabled)

When releasing, ensure:

1. Update `docs/source/conf.py` with new version number
2. Update `CHANGELOG.md` with user-facing changes
3. Build locally and verify: ``uv run --group docs sphinx-build -b html docs/source docs/build/html``
4. Merge to `main` and ReadTheDocs picks up automatically

ReadTheDocs Integration
-----------------------

Configuration is in `readthedocs.yaml`:

.. code-block:: yaml

   version: 2
   python:
     version: "3.11"
     install:
       - method: pip
         path: .
   build:
     os: ubuntu-22.04
     tools:
       sphinx: "7"

Docs build automatically on push to `main`. See `readthedocs.yaml <../../readthedocs.yaml>`_ for details.

Contributing Documentation
--------------------------

**Before submitting a PR with code changes:**

1. Add/update docstrings (Google style)
2. Add examples to docstrings if introducing new user-facing APIs
3. Build docs locally: ``uv run --group docs sphinx-build -b html docs/source docs/build/html``
4. Verify no warnings in build output
5. Open `docs/build/html/index.html` and spot-check the generated API pages

**For new tutorials or guides:**

1. Create `.rst` file in appropriate subdirectory (`tutorials/`, `developer/`, etc.)
2. Add cross-reference in parent index (e.g., `tutorials.rst`)
3. Use clear headings and link to API docs
4. Include code examples (verify they run)
5. Build and verify rendering

Troubleshooting
---------------

**Build fails with "extension not found"**
   Install documentation dependencies: ``uv sync --group docs``.

**Docstring not appearing in generated docs**
   Verify function/class is in ``__all__`` and docstring uses Google format. Run ``uv run --group docs sphinx-build -b html docs/source docs/build/html`` with ``-W`` flag to treat warnings as errors.

**Math equations not rendering**
   Ensure MathJax is enabled in ``conf.py`` and math is wrapped in :math:\` or .. math:: blocks.

**Old content still showing after edit**
   Clear cache: ``rm -rf docs/build`` and rebuild.

**External links broken or outdated**
   Use `linkchecker <https://pypi.org/project/linkchecker/>`_: ``linkchecker docs/build/html/``.

Quick Reference
---------------

**Common Sphinx directives:**

.. code-block:: rst

   .. automodule:: module_name
      :members:
      :undoc-members:

   .. autoclass:: ClassName
      :members:

   .. autofunction:: function_name

   .. note::
      Important note

   .. warning::
      Important warning

   .. code-block:: python
      :linenos:

      code here

Next Steps
----------

- Read `Sphinx official docs <https://www.sphinx-doc.org/>`_ for advanced features
- Review `Furo theme docs <https://pradyunsg.me/furo/>`_ for theme customization
- See :doc:`testing` for testing best practices (also document with examples)
- Check pull requests on GitHub for current documentation work