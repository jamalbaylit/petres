Testing
=======

Petres maintains a comprehensive test suite with **116 tests** across 18 focused modules, achieving systematic coverage of core functionality, edge cases, and integration workflows.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Test Framework
--------------

- **Framework**: `pytest 9.0.2+ <https://docs.pytest.org/>`_ — simple, powerful, extensible
- **Markers**: Automatic categorization by test type (unit, integration, regression, viewer)
- **Fixtures**: Shared reusable test data and grid/zone/interpolator builders
- **Coverage**: `pytest-cov <https://pytest-cov.readthedocs.io/>`_ for line/branch analysis

Quick Start
-----------

**Run all tests:**

.. code-block:: bash

   uv run --group test pytest

**Run fast unit tests only (58 tests, ~0.5s):**

.. code-block:: bash

   uv run --group test pytest -m unit

**Run specific category:**

.. code-block:: bash

   uv run --group test pytest -m integration  # 4 tests
   uv run --group test pytest -m regression   # 4 tests
   uv run --group test pytest -m viewer       # 8 tests

Test Structure
--------------

Tests are organized by functionality:

.. code-block:: text

   tests/
   ├── conftest.py                 # Shared fixtures (8 total)
   ├── grids/
   │   ├── test_pillar_grid.py     # PillarGrid shape, ZCORN, validation (8 unit tests)
   │   └── test_cornerpoint_grid.py # CornerPointGrid, zones, boundaries (10 unit tests)
   ├── horizons/
   │   ├── test_horizon.py              # Horizon creation, intersection, sampling (8 unit)
   │   └── test_horizon_workflows.py    # Picks, shape deformation (3 unit)
   ├── zones/
   │   ├── test_zone.py            # Zone thickness, divide, properties (7 unit)
   │   └── test_zone_levels.py     # Stratigraphic level validation (3 unit)
   ├── interpolators/
   │   ├── test_idw_interpolator.py           # IDW accuracy, KNN, neighbors (12 unit)
   │   ├── test_rbf_interpolator.py           # RBF exact fit, smoothing, 2D/3D (7 unit)
   │   ├── test_kriging_interpolators.py      # OK/UK variance, drift workflows (14 unit)
   │   └── test_interpolator_aliases.py       # Public API contracts (1 unit)
   ├── eclipse/
   │   ├── test_grdecl_io.py        # GRDECL read/write roundtrip (8 unit)
   │   └── test_validation.py       # GRDECL header validation (4 unit)
   ├── properties/
   │   ├── test_grid_properties.py  # Property create/fill/apply (9 unit)
   │   └── test_property_sources.py # Source validation (3 unit)
   ├── viewers/
   │   ├── test_matplotlib2d_viewer_core.py # 2D themes, layers, chaining (3 viewer)
   │   └── test_viewers_optional.py         # Show workflows (5 viewer)
   ├── views/
   │   └── test_view_workflows.py   # 3D horizon/zone/boundary show (3 viewer)
   ├── integration/
   │   ├── test_workflows.py        # Zone→grid→property pipelines (4 integration)
   │   └── test_models_workflows.py # Boundary/Well/Sample lifecycle (3 integration)
   └── regression/
       ├── test_regressions.py              # Edge cases, broadcast shapes (4 regression)
       └── test_zone_and_property_regressions.py # Type safety (2 regression)

**Total: 18 test modules, 116 tests**

Test Categories (Markers)
-------------------------

Tests are tagged with markers for selective execution:

+------------------+--------+--------------------------------------------------------------+
| **Marker**       | **Tests** | **Purpose**                                                    |
+==================+========+==============================================================+
| ``unit``         | 58     | Fast, isolated tests for functions and basic workflows        |
+------------------+--------+--------------------------------------------------------------+
| ``integration``  | 4      | Multi-module workflows (zone→grid, grid→property, etc.)       |
+------------------+--------+--------------------------------------------------------------+
| ``regression``   | 4      | Edge cases and historical bug fixes                           |
+------------------+--------+--------------------------------------------------------------+
| ``viewer``       | 8      | Visualization layer (Matplotlib 2D, PyVista 3D optional)      |
+------------------+--------+--------------------------------------------------------------+

**Run tests by marker:**

.. code-block:: bash

   # Only fast tests
   uv run --group test pytest -m unit

   # Exclude visualization (for CI without pyvista)
   uv run --group test pytest -m "not viewer"

   # Run unit + integration (typical workflow)
   uv run --group test pytest -m "unit or integration"

   # Run only regressions
   uv run --group test pytest -m regression

Shared Fixtures
---------------

All tests use fixtures defined in `tests/conftest.py`. Common fixtures:

**Grid Builders:**

- ``rectilinear_vertices`` — 2D array of vertex coordinates for grid construction
- ``simple_pillar_grid`` — 10×10 grid with uniform pillars (PillarGrid)
- ``simple_cornerpoint_grid`` — 10×10×2 grid with ZCORN values (CornerPointGrid)

**Stratigraphic:**

- ``horizon_plane_top``, ``horizon_plane_base`` — Horizon objects at different depths
- ``continuous_zones`` — 3 continuous zones (no gaps)
- ``gap_zones`` — Zones with stratigraphic gaps

**Well/Boundary:**

- ``sample_wells`` — VerticalWell objects with tops and sample data
- ``boundary_box`` — BoundaryPolygon for grid clipping

**Usage in tests:**

.. code-block:: python

   def test_pillar_grid_shape(simple_pillar_grid):
       assert simple_pillar_grid.shape == (10, 10, 1)

   def test_zone_divide(continuous_zones, simple_cornerpoint_grid):
       zone = continuous_zones[0]
       layers = zone.divide(n_layers=5)  # Build on zone + grid combo
       assert len(layers) == 5

Running Tests with Options
---------------------------

**Verbose output:**

.. code-block:: bash

   uv run --group test pytest -v
   uv run --group test pytest -vv  # Extra verbose (show locals)

**Stop on first failure:**

.. code-block:: bash

   uv run --group test pytest -x

**Run tests matching a name pattern:**

.. code-block:: bash

   uv run --group test pytest -k "interpolator" -v
   uv run --group test pytest -k "not viewer"  # Exclude by pattern

**Run a single test file:**

.. code-block:: bash

   uv run --group test pytest tests/grids/test_pillar_grid.py

**Run a specific test function:**

.. code-block:: bash

   uv run --group test pytest tests/grids/test_pillar_grid.py::test_pillar_grid_shape

**Parallel execution** (requires ``pytest-xdist``):

.. code-block:: bash

   uv run --group test pytest -n auto  # Use all CPU cores

**Run last failed:**

.. code-block:: bash

   uv run --group test pytest --lf

**Run with timeout** (requires ``pytest-timeout``):

.. code-block:: bash

   uv run --group test pytest --timeout=10

Coverage Reports
----------------

**Generate coverage metrics:**

.. code-block:: bash

   uv run --group test pytest --cov=petres --cov-report=term-missing

**Create HTML report:**

.. code-block:: bash

   uv run --group test pytest --cov=petres --cov-report=html

Open ``htmlcov/index.html`` in a browser to view line coverage by module.

**Check coverage of specific modules:**

.. code-block:: bash

   uv run --group test pytest --cov=petres.grids tests/grids/ --cov-report=term

Writing Tests
-------------

General Guidelines
^^^^^^^^^^^^^^^^^^

1. **Keep tests focused** — one logical assertion per test, or grouped related assertions
2. **Use fixtures** — prefer fixtures over setup/teardown methods
3. **Use descriptive names** — test function names should state what is being tested
4. **Avoid mocks when possible** — test real objects with real data where practical
5. **Test edge cases** — empty inputs, boundary values, invalid parameters
6. **Include docstrings** — explain non-obvious test logic

Example: Grid Shape Test
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   """Test CornerPointGrid shape consistency."""

   def test_cornerpoint_grid_shape_consistency(simple_cornerpoint_grid):
       """Verify CornerPointGrid reports correct dimensions."""
       # Arrange
       grid = simple_cornerpoint_grid
       expected_shape = (10, 10, 2)

       # Act
       actual_shape = grid.shape

       # Assert
       assert actual_shape == expected_shape

Unit Test Best Practices
^^^^^^^^^^^^^^^^^^^^^^^^

- **Isolation**: Each test should be independent; don't rely on test execution order
- **Speed**: Unit tests should complete in <1ms. Avoid I/O, networking, heavy computation
- **Clarity**: Use meaningful variable names; avoid magic numbers

.. code-block:: python

   def test_idw_interpolator_power_validation():
       """IDW constructor rejects power <= 0."""
       with pytest.raises(ValueError, match=r"power.*positive"):
           IDWInterpolator(power=-1)

Integration Test Best Practices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Realistic workflows**: Test how users actually combine components
- **Data flow** → Act/Assert multiple objects sequentially
- **State changes**: Verify side effects are correct

.. code-block:: python

   def test_zone_divide_and_apply_property(
       continuous_zones,
       simple_cornerpoint_grid,
       sample_wells,
   ):
       """Test workflow: divide zone → fill property grid with zone levels."""
       # Divide zone into 5 layers
       zone = continuous_zones[0]
       layers = zone.divide(n_layers=5)
       assert len(layers) == 5

       # Create property from zone level
       prop = petres.GridProperty.from_zone_level(grid, zone, 0)
       assert prop.grid == grid
       assert prop.data.shape == grid.shape

Regression Test Best Practices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Document the bug**: Add a comment referencing the issue
- **Include minimal reproduction**: smallest data that triggers the bug
- **Verify fix**: assert the corrected behavior

.. code-block:: python

   def test_regression_actnum_broadcast_shape():
       """Regression: ACTNUM array shape mismatch with non-cubic grids.
       
       Issue: https://github.com/jamalbaylit/petres/issues/42
       """
       grid = simple_cornerpoint_grid
       actnum = np.zeros(grid.shape, dtype=bool)
       actnum[:, :, 0] = True  # Only top layer active

       # Should not raise shape error
       grid.actnum = actnum
       assert grid.actnum.shape == grid.shape

Visualization Test Best Practices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- **Marker tests as ``@pytest.mark.viewer``** so they can be skipped in headless CI
- **Import optional dependencies carefully**:

.. code-block:: python

   import pytest

   @pytest.mark.viewer
   def test_matplotlib2d_viewer_show(simple_cornerpoint_grid):
       """Test Matplotlib 2D viewer show workflow."""
       viewer = petres.Matplotlib2DViewer()
       viewer.add_grid(simple_cornerpoint_grid)
       # Don't call show() in headless; verify object state instead
       assert viewer.grid is not None

Testing Interpolators
^^^^^^^^^^^^^^^^^^^^^

All four interpolator types are tested:

- **IDW**: Inverse Distance Weighting — tests power, neighbors, KNN sorting
- **RBF**: Radial Basis Functions — tests smoothing, radius, 2D/3D geometry
- **OK**: Ordinary Kriging — tests variance API, 2D/3D support, configuration
- **UK**: Universal Kriging — tests drift types (functional, specified, point-log), variance

Each interpolator validates:

1. **Constructor errors** — invalid parameters reject early with clear messages
2. **Fit behavior** — handles duplicates, insufficient data, shape mismatches
3. **Predict behavior** — interpolates correctly, handles empty queries
4. **Variance API** — kriging variance computed when requested
5. **Dimensional consistency** — 2D vs 3D coordinate arrays enforced

.. code-block:: bash

   # Run all interpolator tests (34 tests)
   uv run --group test pytest tests/interpolators/ -v

Common Assertions
-----------------

**Numeric comparisons:**

.. code-block:: python

   import numpy as np
   from numpy.testing import assert_allclose

   # Floating point comparison with tolerance
   assert_allclose(actual, expected, rtol=1e-10, atol=1e-12)

   # Check array shape and dtype
   assert result.shape == (10, 10, 2)
   assert result.dtype == np.float32

**Exception handling:**

.. code-block:: python

   import pytest

   # Verify exception type and message pattern
   with pytest.raises(ValueError, match=r"parameter.*expected"):
       function_under_test()

**Boolean checks:**

.. code-block:: python

   assert np.all(active_cells)
   assert np.any(np.isnan(data))

Debugging Tests
---------------

**Run with print statements visible:**

.. code-block:: bash

   uv run --group test pytest -s

**Drop into debugger on failure:**

.. code-block:: bash

   uv run --group test pytest --pdb

**Show local variables on failure:**

.. code-block:: bash

   uv run --group test pytest -vv --showlocals

**Generate JUnit XML for CI:**

.. code-block:: bash

   uv run --group test pytest --junit-xml=test-results.xml

Continuous Integration
----------------------

Tests run automatically on GitHub Actions:

- **Trigger**: Push to `dev`/`main` or PR
- **Matrix**: Python 3.11, 3.12, 3.13 on Ubuntu + Windows
- **Optional**: Python 3.14 experimental on Ubuntu (allowed to fail)
- **Markers**: Markers enable selective test execution in parallel CI jobs

See `.github/workflows/ci.yml <../../.github/workflows/ci.yml>`_ for full CI configuration.

Troubleshooting
---------------

**Tests pass locally but fail in CI**
   Check Python version (`uv run python --version`). Petres supports 3.11+. Run `uv sync --python 3.11` to test older versions.

**Import errors in tests**
   Ensure all dependencies are installed: ``uv sync --group dev --group test``. Check `pyproject.toml` for optional dependencies.

**Pykrige tests skipped**
   Kriging tests are optional (skip if pykrige unavailable). Install: ``uv pip install pykrige``.

**Slow test runs**
   Use markers to skip test categories: ``pytest -m "unit or integration"`` excludes visualization tests.

**Fixture not found error**
   Ensure `tests/conftest.py` exists and is properly formatted. Fixture scope and dependencies must be correct.

Next Steps
----------

- Submit a test alongside your code changes (test-driven development)
- Ensure test passes both locally and in CI before opening a PR
- Reference related issues in regression tests
- See :doc:`documentation` for docstring standards in tested functions