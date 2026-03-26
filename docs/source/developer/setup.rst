Developer Setup
===============

This section describes how to set up a local development environment
for Petres.

Prerequisites
-------------

- Python >= 3.11
- `uv <https://github.com/astral-sh/uv>`_ installed

Clone the Repository
--------------------

.. code-block:: bash

   git clone https://github.com/jamalbaylit/petres.git
   cd petres

Install Development Environment
-------------------------------

Install all development, testing, and documentation dependencies:

.. code-block:: bash

   uv sync --group dev --group test --group docs

This installs:

- Development tools (ruff, mypy, build)
- Testing tools (pytest, pytest-cov)
- Documentation tools (sphinx, furo, etc.)

Editable Installation
---------------------

The project is installed in editable mode automatically via ``uv sync``.

This allows local changes to be reflected immediately without reinstalling.

Verify Installation
-------------------

.. code-block:: bash

   uv run python -c "import petres; print(petres.__version__)"

Run Tests
---------

Run the full test suite:

.. code-block:: bash

   uv run --group test pytest

Run only fast unit tests:

.. code-block:: bash

   uv run --group test pytest -m unit

Run integration and regression subsets:

.. code-block:: bash

   uv run --group test pytest -m integration
   uv run --group test pytest -m regression

Run viewer-related tests (optional visualization dependencies):

.. code-block:: bash

   uv run --group test pytest -m viewer