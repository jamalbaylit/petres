Developer Setup
===============

This guide walks through setting up **Petres** for local development. The project uses modern Python tooling for dependency management, code quality, testing, and documentation.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Prerequisites
-------------

**Required:**

- **Python 3.11+** (3.11, 3.12, 3.13 tested; 3.14 experimental)
- **uv** (`astral-sh/uv <https://docs.astral.sh/uv/>`_) — fast, reliable Python package installer and manager

**Optional (recommended):**

- **Git** for version control
- **VS Code** with Python extension for IDE support
- **make** or **PowerShell** for script execution

Install uv
----------

If you don't have ``uv`` installed, follow the `installation guide <https://docs.astral.sh/uv/getting-started/installation/>`_:

.. tabs::

   .. tab:: macOS / Linux

      .. code-block:: bash

         curl -LsSf https://astral.sh/uv/install.sh | sh

   .. tab:: Windows (PowerShell)

      .. code-block:: powershell

         irm https://astral.sh/uv/install.ps1 | iex

   .. tab:: Homebrew

      .. code-block:: bash

         brew install uv

Verify installation:

.. code-block:: bash

   uv --version

Clone the Repository
--------------------

.. code-block:: bash

   git clone https://github.com/jamalbaylit/petres.git
   cd petres

Install Development Environment
-------------------------------

**Single command to install all dependencies:**

.. code-block:: bash

   uv sync --group dev --group test --group docs

This creates a virtual environment and installs:

- **Core dependencies**: NumPy, SciPy, scikit-learn, pyvista, matplotlib
- **Dev tools**: Ruff (linting/formatting), PyTest, PyTest-Cov, Black, MyPy
- **Testing**: pytest 9.0.2+, pytest-cov, scipy-spatial
- **Documentation**: Sphinx, Furo theme, sphinx-autodoc-typehints
- **Optional**: pykrige (for kriging interpolators), netCDF4, pyresample

Python Environment Activation
-----------------------------

The virtual environment is automatically created by ``uv sync``. To activate it:

.. tabs::

   .. tab:: macOS / Linux (bash/zsh)

      .. code-block:: bash

         source .venv/bin/activate

   .. tab:: Windows (PowerShell)

      .. code-block:: powershell

         .\.venv\Scripts\Activate.ps1

   .. tab:: Windows (cmd)

      .. code-block:: cmd

         .venv\Scripts\activate.bat

Or use ``uv run`` to execute commands in the environment without explicit activation:

.. code-block:: bash

   uv run python --version
   uv run pytest

Verify Installation
-------------------

Confirm Petres is installed and accessible:

.. code-block:: bash

   uv run python -c "import petres; print(f'Petres {petres.__version__} ready')"

Expected output:

.. code-block:: text

   Petres 0.X.X ready

IDE Configuration (VS Code)
---------------------------

For seamless development in VS Code:

1. **Open the workspace folder:**
   - File → Open Folder → select ``petres`` directory

2. **Select the Python interpreter:**
   - Ctrl+Shift+P (or Cmd+Shift+P on Mac)
   - Type "Python: Select Interpreter"
   - Choose the ``.venv`` environment created by ``uv``

3. **Recommended extensions:**
   - `Python <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_
   - `Pylance <https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance>`_ (language server)
   - `Ruff <https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff>`_ (fast linting)

3. **Configure workspace settings** (`.vscode/settings.json`):

   .. code-block:: json

      {
        "[python]": {
          "editor.formatOnSave": true,
          "editor.defaultFormatter": "charliermarsh.ruff"
        },
        "python.linting.enabled": true
      }

Code Quality Tools
------------------

Ruff: Linting and Formatting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Format all code** (integrates 50+ linting rules + Black formatting):

.. code-block:: bash

   uv run ruff format src tests docs

**Check for linting violations:**

.. code-block:: bash

   uv run ruff check src tests docs

**Fix auto-fixable violations:**

.. code-block:: bash

   uv run ruff check --fix src tests docs

MyPy: Static Type Checking
^^^^^^^^^^^^^^^^^^^^^^^^^^

Verify type annotations are correct:

.. code-block:: bash

   uv run mypy src/petres

Common issues and fixes:

.. code-block:: bash

   # Include reveal types for debugging
   uv run mypy src/petres --show-column-numbers --pretty

See `pyproject.toml <../pyproject.toml>`_ for MyPy configuration (``[tool.mypy]``).

Run Tests
---------

**Run all tests:**

.. code-block:: bash

   uv run --group test pytest

**Run tests by category** (using pytest markers):

.. code-block:: bash

   # Fast unit tests only (58 tests)
   uv run --group test pytest -m unit

   # Integration tests (4 tests)
   uv run --group test pytest -m integration

   # Regression tests (4 tests)
   uv run --group test pytest -m regression

   # Visualization tests (8 tests)
   uv run --group test pytest -m viewer

**Run with verbose output:**

.. code-block:: bash

   uv run --group test pytest -v

**Run specific test file:**

.. code-block:: bash

   uv run --group test pytest tests/grids/test_pillar_grid.py

**Run tests matching pattern:**

.. code-block:: bash

   uv run --group test pytest -k "interpolator" -v

**Generate coverage report:**

.. code-block:: bash

   uv run --group test pytest --cov=petres --cov-report=html --cov-report=term-missing

For detailed testing guidance, see :doc:`testing`.

Pre-commit Hooks (Optional)
---------------------------

Automatically check code before committing:

.. code-block:: bash

   uv pip install pre-commit
   pre-commit install
   pre-commit run --all-files

This runs ruff formatting and type checking on staged files. Configuration is in `.pre-commit-config.yaml`.

Build Documentation Locally
---------------------------

**Build HTML documentation:**

.. code-block:: bash

   uv run --group docs sphinx-build -b html docs/source docs/build/html

**Open in browser:**

.. tabs::

   .. tab:: macOS / Linux

      .. code-block:: bash

         open docs/build/html/index.html

   .. tab:: Windows (PowerShell)

      .. code-block:: powershell

         Start-Process docs/build/html/index.html

**Live reload during development:**

.. code-block:: bash

   uv run --group docs sphinx-autobuild docs/source docs/build/html

The docs server watches for changes and rebuilds automatically. Browse to ``http://127.0.0.1:8000``.

See :doc:`documentation` for documentation guidelines.

Troubleshooting
---------------

**"uv: command not found"**
   Ensure ``uv`` is in your PATH. Run the installation command again or check your shell configuration.

**"ModuleNotFoundError: No module named 'petres'"**
   Run ``uv sync --group dev --group test`` to install dependencies. Ensure the ``.venv`` environment is active.

**Tests fail with "ImportError: pykrige"**
   Kriging tests are skipped if ``pykrige`` is unavailable. It's optional. For kriging support: ``uv pip install pykrige``.

**Ruff or MyPy fails unexpectedly**
   Clear cache and reinstall: ``rm -rf .ruff_cache && uv sync --reinstall-package petres``.

**Documentation build takes too long**
   Use ``sphinx-autodoc-typehints`` sparingly. Clear build cache: ``rm -rf docs/build``.

Next Steps
----------

- Read the :doc:`testing` guide to understand the test structure and best practices
- Explore :doc:`documentation` for writing high-quality docstrings and API docs
- Check `CONTRIBUTING.md <../../CONTRIBUTING.md>`_ for contribution workflow (PR/review process)
- See the `GitHub Actions workflow <../../.github/workflows/ci.yml>`_ for automated CI setup