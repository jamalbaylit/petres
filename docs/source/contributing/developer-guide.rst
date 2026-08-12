Developer Guide
===============

Thank you for your interest in contributing to Petres.
Contributions of all sizes are welcome, including bug reports, 
feature requests, documentation improvements, tests, examples, and new functionality.

Before contributing, please take a few minutes to read this guide. 
Following these guidelines helps maintain consistency and makes the review process smoother for everyone.


Quick Facts
-----------

- **Package Name:** `petres`
- **Supported Python Versions:** 3.10 - 3.14
- **Build System:** `setuptools` with `setuptools-scm` for versioning
- **Dependency Manager:** `uv`
- **Documentation:** `Sphinx-based`, deployed via `ReadTheDocs`
- **Testing Framework:** `pytest` with markers for categorization
- **Primary Domain:** Static reservoir modeling in reservoir simulation engineering


Development Setup
-----------------

For contribution to Petres, create your own copy of the repository (a
*fork*), set up a local development environment, and install the
development dependencies.

Fork and Clone the Repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`Fork <https://github.com/jamalbaylit/petres/fork>`_ the repository to create your own copy in your GitHub account, then clone it locally:

.. code-block:: bash

   git clone https://github.com/<your-username>/petres.git
   cd petres

Verify the configured remotes:

.. code-block:: bash

   git remote -v

You should see your fork listed as origin. If the original Petres repository is not listed as upstream, add it manually:

.. code-block:: bash

   git remote add upstream https://github.com/jamalbaylit/petres.git

Verify the remotes again to ensure both origin (your fork) and upstream (the original repository) are configured correctly.


Create a Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This project uses `uv <https://github.com/astral-sh/uv>`_ for dependency management and development environments.
Before proceeding, ensure that it is installed on your system.

Development is standardized on Python **3.13** version, as defined in the ``.python-version`` file.
To create the development environment and install all dependencies, run:

.. code-block:: bash

   uv sync --dev

If the required Python version is not already installed, `uv` will automatically download and use it. You may also install it explicitly beforehand:

.. code-block:: bash

   uv python install 3.13


Development Workflow
--------------------

Create a Branch
^^^^^^^^^^^^^^^

Create a dedicated branch from the latest ``dev`` branch for your contribution.
Before creating a branch, ensure your local ``dev`` branch is up to date:

.. code-block:: bash

   git checkout dev
   git pull upstream dev
   git checkout -b feature/my-feature

Branch names must follow a consistent convention to keep the repository organized and reviewable.
Use the following prefixes:

.. code-block:: text

   feature/<short-description>        # new features
   improvement/<short-description>    # enhancements to existing features
   bugfix/<short-description>         # bug fixes
   hotfix/<short-description>         # urgent fixes
   refactor/<short-description>       # code refactoring without behavior change
   docs/<short-description>           # documentation updates
   test/<short-description>           # adding or updating tests
   ci/<short-description>             # CI/CD changes

Rules for branch names:

- Use lowercase letters only
- Use hyphens (-) to separate words
- Keep the description short and meaningful

Examples:

.. code-block:: text

   feature/add-grid-export
   feature/property-upscaling
   bugfix/fault-handling


Make Changes
^^^^^^^^^^^^

Implement your changes following the coding standards defined in the project style guide.
Keep changes focused and avoid mixing unrelated modifications in a single commit or pull request.
Before submitting a pull request, ensure all tests pass (see :ref:`running-tests`) and that the documentation builds successfully (see :ref:`building-documentation`).

Commit and Pull Request
^^^^^^^^^^^^^^^^^^^^^^^

Keep commits focused and atomic. Prefer multiple small, meaningful commits over large mixed changes.

Each commit message must include a mandatory summary line written in sentence case.
This line should clearly describe the purpose of the change and must be meaningful on its own.
If needed, additional details can be provided in the commit body using hyphens (-) for bullet points:

.. code-block:: text

   Fix invalid input handling in fault module

   - Validate null and empty inputs
   - Improve error messages for debugging
   - Prevent crash on malformed data

Stay up to date with the base branch during development when needed:

.. code-block:: bash

   git fetch upstream
   git rebase upstream/dev

Push changes to your fork (not upstream):

.. code-block:: bash

   git push origin feature/my-feature

Then open a pull request from your fork to upstream using the web interface (e.g. GitHub UI):

- Base repository: upstream
- Base branch: ``dev``
- Compare branch: your feature branch

Only merge after all checks pass.


Dependency Management
---------------------

This project organizes dependencies into groups based on their purpose.

+------------+---------------------------------------------------------+
| Group      | Purpose                                                 |
+============+=========================================================+
| docs       | Packages required to build and maintain the             |
|            | documentation.                                          |
+------------+---------------------------------------------------------+
| test       | Packages used for testing, validation, and test         |
|            | infrastructure.                                         |
+------------+---------------------------------------------------------+
| examples   | Packages used only in examples, tutorials, and          |
|            | notebooks.                                              |
+------------+---------------------------------------------------------+
| dev        | Convenience group that installs ``docs``, ``test``,     |
|            | and ``examples`` dependencies together.                 |
+------------+---------------------------------------------------------+

When adding a new dependency, first determine whether it is required by
library itself or only by a specific development workflow.
If the package is required for the core functionality of Petres, add it as
a core dependency:

.. code-block:: bash

   uv add <package>

Otherwise, add it to the dependency group that best matches its purpose:

.. code-block:: bash

   uv add --group <group-name> <package>

.. important::

   The ``dev`` group is an aggregate convenience group and must not contain
   direct dependencies. Always add new packages to the specific group that
   requires them (``docs``, ``test``, or ``examples``).


Repository Structure
--------------------

The repository is organized into source code, tests, documentation, and supporting assets:

.. code-block:: text

   petres/
   ├── src/petres/       # Main Python package
   ├── tests/            # Automated tests (unit, integration, regression)
   ├── docs/             # Documentation (source and build output)
   ├── examples/         # Usage examples
   ├── data/             # Sample and reference datasets
   ├── assets/           # Static assets (images, logos, etc.)
   ├── scripts/          # Utility and automation scripts
   ├── pyproject.toml    # Project configuration
   ├── README.md
   └── LICENSE


Adding New Features
-------------------

The ``src/petres`` package is the canonical location for library code.
New features and enhancements should be implemented here.

The library is organized into focused subpackages to keep responsibilities
clear and make the codebase intuitive to navigate.

- ``config/`` — Library configuration.
- ``eclipse/`` — Eclipse readers, writers, and related functionality.
- ``errors/`` — Centralized exception classes and error utilities. Add new
  exception types here instead of defining ad-hoc exceptions elsewhere.
- ``grids/`` — Grid data structures, creation utilities, and algorithms.
  New grid types, grid import/export functionality, and cell operations
  belong here.
- ``interpolators/`` — Interpolation algorithms and supporting utilities.
  Implement each interpolation method in its own module and register it in
  ``interpolators/__init__.py``.
- ``models/`` — Reservoir and domain models such as wells, zones, and
  horizons.
- ``viewers/`` — Visualization backends and viewer utilities. Backend-
  specific integrations (for example, PyVista or Matplotlib) belong here.
- ``_utils/`` — Internal helper functions and small utilities that are not
  part of the public API.
- ``_compat.py`` and ``_validation.py`` — Shared compatibility and input
  validation utilities.

Modules and packages whose names begin with ``_`` are considered internal
implementation details. Public API is defined by the names that are exported
from package ``__init__.py`` files and listed in ``__all__``. If a symbol is
intended for users, it must be re-exported through the relevant ``__init__.py``
and included in ``__all__``.

.. note::

   Each subpackage may define its own internal helper modules. These helpers
   are intended for use only within their respective subpackage and should not
   be imported by other subpackages unless absolutely necessary.

When adding a new feature, follow these guidelines:

- Choose the appropriate subpackage whose primary responsibility best matches the feature (``grids``, ``interpolators``, ``viewers``, etc.). Each feature should have a single, well-defined home. Avoid duplicating logic, algorithms, or data structures across subpackages. If multiple subpackages require shared functionality, implement it once in the subpackage that owns the core abstraction and reuse it where necessary. If no existing subpackage is suitable, create a new one with a short, descriptive, and intuitive name.

- Determine public API exposure: if the feature is intended for public use, ensure it is re-exported from the relevant ``__init__.py`` and included in ``__all__`` list.

- Avoid duplication of logic across the codebase by reusing existing implementations whenever possible.

- If the feature introduces a new class, ensure it is consistent with the existing class hierarchy defined in the :ref:`Architecture Patterns <architecture-patterns>` section. Prefer extending or reusing existing base classes and structures. However, if the new functionality does not naturally fit into any existing hierarchy, it is acceptable to introduce a new, well-justified hierarchy, provided it follows the same design principles and overall architectural consistency.

- Add or update the relevant documentation for all user-facing functionality.

- Add tests covering the new feature, including edge cases where relevant.

- Provide a runnable example under ``examples/`` demonstrating typical usage. Keep examples concise, reproducible, and focused on a single concept.

- Ensure that all implemented code follows the coding standards defined in the :ref:`Coding Standards <coding-standards>` section, including naming conventions, structure, and formatting rules.


.. important::

   Before introducing major architectural changes, open an issue or discussion first.
   Clearly explain the motivation and expected impact.

.. _coding-standards:

Coding Standards
----------------

This section defines the coding conventions and general principles used in the project.
All contributions must follow these guidelines to ensure consistency and maintainability.

The following guidelines apply to all Python code in Petres:

- Follow PEP 8 for Python code style. See :ref:`naming-conventions` and general formatting rules below.
- Prefer readability over clever or overly compact implementations.
- Keep code simple and explicit.
- Avoid unnecessary complexity and premature optimization.
- Avoid circular imports; if unavoidable, use local imports within functions or methods.
- Use type hints for public APIs where practical. See :ref:`type-hints`.
- All public APIs must include NumPy-style docstrings. See :ref:`docstrings`.



.. _naming-conventions:

Naming Conventions
^^^^^^^^^^^^^^^^^^

The following naming conventions are used consistently across the codebase to ensure readability and maintainability.

===================== ========================= ======================
Element               Convention                Example
===================== ========================= ======================
Classes               PascalCase                DataLoader
Functions             snake_case                compute_value
Variables             snake_case                file_path
Constants             UPPER_CASE                DEFAULT_TIMEOUT
Internal attributes   _leading_underscore       _internal_cache
===================== ========================= ======================


.. _type-hints:

Type Hints
^^^^^^^^^^

Use type hints on all public APIs. Prefer clarity over cleverness.

Recommended patterns:

- Use ``str | None`` for optional values
- Use ``list[T]`` / ``tuple[T, ...]`` / ``dict[K, V]`` for built-in collections
- Use ``Sequence[T]`` for read-only inputs
- Use ``NDArray[np.float64]`` for NumPy arrays when dtype matters
- Use ``Literal[...]`` for fixed string options
- Use ``@overload`` when a function has multiple valid signatures

Examples:

.. code-block:: python

   from typing import Literal, Sequence
   from numpy.typing import NDArray
   import numpy as np

   def interpolate_property(
      grid: CornerPointGrid,
      values: NDArray[np.float64],
      method: Literal["idw", "rbf", "kriging"] = "idw",
   ) -> GridProperty:
      ...

   def create_cornerpoint_grid(
      vertices: NDArray[np.float64],
      horizons: Sequence[Horizon],
   ) -> CornerPointGrid:
      ...

.. _docstrings:

Docstrings
^^^^^^^^^^

Petres uses **NumPy-style docstrings** for all public APIs. 
Docstrings should be clear, concise, and focused on behavior 
rather than repeating type hints. Recommended section order:

- Summary — one-line description of the function or class purpose.
- Extended summary (optional) — additional context when needed.
- Parameters — describe inputs, including types and shapes when relevant.
- Returns — describe output type, shape, and meaning.
- Raises — list exceptions and when they occur.
- Notes — include assumptions, limitations, or implementation details.
- See Also — related functions, classes, or concepts.
- Examples — short, runnable usage examples.

Example:

.. code-block:: python

   def compute_cell_volumes(grid: CornerPointGrid) -> NDArray[np.float64]:
      """Compute cell volumes for a corner-point grid.

      Parameters
      ----------
      grid : CornerPointGrid
         The structured corner-point grid.

      Returns
      -------
      ndarray of float64
         Cell volumes with shape (nx, ny, nz).

      Raises
      ------
      ValueError
         If the grid is invalid.

      Examples
      --------
      >>> volumes = compute_cell_volumes(grid)
      >>> volumes.shape
      (grid.nx, grid.ny, grid.nz)
      """



.. _running-tests:

Running Tests
-------------

You can run the full test suite using either the Makefile or ``uv``:

.. code-block:: bash

   # Using Makefile
   make test

   # Or directly with uv
   uv run --group test pytest


Test Categories
^^^^^^^^^^^^^^^

Tests are automatically marked via ``conftest.py`` based on their folder structure:

================== ============================================================
Marker             Description
================== ============================================================
unit               Fast, module-level tests (default)
integration        Multi-module workflows
regression         Known edge cases and bug reproductions
viewer             Visualization-related tests (slow, optional dependencies)
================== ============================================================

Run specific test groups using pytest markers:

.. code-block:: bash

   # Run only unit tests
   uv run --group test pytest -m unit

   # Run only integration tests
   uv run --group test pytest -m integration

   # Exclude viewer tests
   uv run --group test pytest -m "not viewer"


.. _building-documentation:

Building Documentation
----------------------

You can build the documentation locally using the Makefile command below. This will generate the HTML output inside the build directory.

.. code-block:: bash

   make docs

   # Output directory
   docs/build/html/

   # Open in browser
   docs/build/html/index.html

The documentation source files are located under ``docs/source/``. This directory contains all guides, API references, examples, and Sphinx configuration used to generate the final docs.

.. code-block:: text

   docs/source/
   ├── index.rst              Main landing page
   ├── getting-started/       Installation and quickstart guides
   ├── fundamentals/          Core concepts (grids, corner-point geometry)
   ├── tutorials/             Feature-focused walkthroughs
   ├── examples/              Auto-generated from example scripts
   ├── api/                  Auto-generated API reference
   ├── _ext/                 Custom Sphinx extensions
   │   ├── apigen.py         API structure generator
   │   └── exampledocs.py    Example embedding system
   └── _config/              Shared Sphinx configuration


.. _architecture-patterns:

Architecture Patterns
---------------------

This section summarizes the main inheritance hierarchies and core architectural building blocks of the library.
It highlights error handling structures, interpolation framework, visualization backends, and key public API classes.

Error Hierarchy
^^^^^^^^^^^^^^^

.. code-block:: text

   PetresError (Exception)
   ├── VisualizationError
   ├── ExportError
   ├── GridError
   │   └── UnsupportedGridAttributeError
   ├── PropertyError
   │   ├── MissingEclipseKeywordError
   │   ├── MissingPropertyValueError
   │   ├── ReservedPropertyNameError
   │   └── ExistingPropertyNameError
   ├── HorizonError
   ├── ZoneError
   ├── InterpolationError
   └── EclipseError
      └── GRDECLExportError
         └── GRDECLMissingValueError

Interpolation Framework
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

   BaseInterpolator (ABC)
   ├── InverseDistanceWeightingInterpolator
   ├── RadialBasisFunctionInterpolator
   └── BasePyKrigeInterpolator
      ├── OrdinaryKrigingInterpolator
      └── UniversalKrigingInterpolator

Visualization Framework
^^^^^^^^^^^^^^^^^^^^^^^

2D Viewer:

.. code-block:: text

   Base2DViewer (ABC)
   └── Matplotlib2DViewer

3D Viewer:

.. code-block:: text

   Base3DViewer (ABC)
   └── PyVista3DViewer

   Base3DViewerTheme (ABC)
   └── PyVista3DViewerTheme
