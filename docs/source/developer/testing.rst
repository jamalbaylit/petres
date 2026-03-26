Testing
=======

Petres uses ``pytest`` for testing.

Run All Tests
-------------

.. code-block:: bash

   uv run --group test pytest

Run Specific Test Categories
----------------------------

Tests are organized using markers:

- ``unit`` → fast, isolated logic tests
- ``io`` → file I/O (GRDECL, etc.)
- ``integration`` → full workflows
- ``visualization`` → optional PyVista tests

Examples:

.. code-block:: bash

   # Fast tests only
   uv run pytest -m "unit or io"

   # Skip visualization tests
   uv run pytest -m "not visualization"

   # Run integration tests only
   uv run pytest -m integration

Coverage
--------

.. code-block:: bash

   uv run pytest --cov=petres --cov-report=term-missing

Test Structure
--------------

Tests are organized as follows:

.. code-block:: text

   tests/
     unit/
     io/
     integration/
     visualization/

Guidelines
----------

- Prefer **small, deterministic unit tests**
- Add **round-trip tests** for I/O (read → write → read)
- Include **integration tests** for complete workflows
- Avoid heavy visualization logic in core test suite