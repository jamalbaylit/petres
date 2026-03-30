Contributing to Petres
======================

Thank you for your interest in contributing to Petres! This guide covers the entire contribution workflow, from setup through pull request review. We welcome bug reports, feature requests, documentation improvements, and code contributions.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Code of Conduct
---------------

Petres is committed to providing a welcoming and respectful community environment. We expect all contributors to:

- Be respectful and inclusive
- Focus on constructive criticism and ideas
- Report harassment or unacceptable behavior to the maintainers

For the full Code of Conduct, see `CODE_OF_CONDUCT.md <../../CODE_OF_CONDUCT.md>`_.

Getting Started
---------------

**1. Fork the repository:**

- Click "Fork" on https://github.com/jamalbaylit/petres
- Clone your fork locally:

.. code-block:: bash

   git clone https://github.com/<your-username>/petres.git
   cd petres

**2. Add upstream remote:**

.. code-block:: bash

   git remote add upstream https://github.com/jamalbaylit/petres.git

**3. Set up development environment:**

.. code-block:: bash

   uv sync --group dev --group test --group docs

See :doc:`setup` for detailed setup instructions.

**4. Create a branch:**

Use a descriptive branch name that reflects the work:

.. code-block:: bash

   # Bug fix
   git checkout -b fix/issue-123-grid-shape-validation

   # Feature
   git checkout -b feature/kriging-interpolator-support

   # Documentation
   git checkout -b docs/add-grid-tutorial

Branch Naming Convention
------------------------

- **``fix/``** — bug fixes (commit message: "Fix: ...")
- **``feature/``** — new features (commit message: "Feature: ...")
- **``docs/``** — documentation only (commit message: "Docs: ...")
- **``refactor/``** — code refactoring (commit message: "Refactor: ...")
- **``test/``** — test additions (commit message: "Test: ...")

Making Changes
--------------

Before you start, understand the scope of your contribution:

Types of Contributions
^^^^^^^^^^^^^^^^^^^^^^

**Bug Reports**
   Report issues on `GitHub Issues <https://github.com/jamalbaylit/petres/issues>`_. Include:
   - Python version and OS
   - Minimal code to reproduce
   - Expected vs actual behavior
   - Error traceback (if applicable)

**Feature Requests**
   Open an issue describing:
   - What you want to build and why
   - How it fits into the library
   - Example usage (pseudocode is fine)
   - Potential performance implications

**Bug Fixes**
   - Create an issue first (or reference existing issue)
   - Implement fix with tests
   - Reference issue in PR (``Closes #123``)

**New Features**
   - Open a discussion issue first to align with maintainers
   - Implement with comprehensive tests
   - Document with docstrings and examples
   - Update CHANGELOG

**Documentation Improvements**
   - Typos, clarity, or missing examples
   - New tutorials or guides
   - Improved API docs
   - No PR discussion needed; just submit!

Code Style
----------

Petres follows strict code quality standards to ensure readability and maintainability.

Formatting with Ruff
^^^^^^^^^^^^^^^^^^^^

Automatically format all code:

.. code-block:: bash

   uv run ruff format src tests docs

Fix auto-fixable linting issues:

.. code-block:: bash

   uv run ruff check --fix src tests docs

**Before committing, always format** your changes:

.. code-block:: bash

   git add .
   uv run ruff format src tests docs
   git add .  # Stage formatting changes
   git commit -m "Fix: issue description"

Type Hints
^^^^^^^^^^

All public functions must have type hints. Examples:

.. code-block:: python

   # Correct
   def compute_volume(
       grid: CornerPointGrid,
       units: str = "m3",
   ) -> NDArray[np.float64]:
       """Compute cell volumes."""
       ...

   # Incorrect (missing type hints)
   def compute_volume(grid, units="m3"):
       """Compute cell volumes."""
       ...

Run MyPy type checker:

.. code-block:: bash

   uv run mypy src/petres

Docstrings
^^^^^^^^^^

Follow Google-style docstrings (see :doc:`documentation` for full guide):

.. code-block:: python

   def create_cornerpoint_grid(
       vertices: NDArray,
       horizons: Sequence[Horizon],
   ) -> CornerPointGrid:
       """Create a corner-point grid from vertices and horizons.

       A brief description of what the function does.

       Args:
           vertices: Mesh grid vertices, shape (nx+1, ny+1, 2).
           horizons: Sequence of Horizon objects.

       Returns:
           CornerPointGrid: The created grid ready for use.

       Raises:
           ValueError: If horizons are not sorted by depth.

       Examples:
           .. code-block:: python

               grid = create_cornerpoint_grid(vertices, horizons)
       """

Import Organization
^^^^^^^^^^^^^^^^^^^

Organize imports as:

#. Standard library (``os``, ``sys``, ``pathlib``, etc.)
#. Third-party imports (``numpy``, ``scipy``, ``sklearn``, etc.)
#. Local imports (``from . import core``, etc.)

Separate sections with blank lines:

.. code-block:: python

   import os
   from pathlib import Path
   from typing import Sequence, Optional

   import numpy as np
   from numpy.typing import NDArray
   import scipy.interpolate

   from ._core import CornerPointGrid
   from .interpolators import IDWInterpolator

Testing
-------

All code changes must include tests. See :doc:`testing` for comprehensive guidelines.

**Test Requirements:**

1. **Unit tests** for new functions/methods
2. **Integration tests** for workflows combining multiple components
3. **Edge case tests** for boundary conditions, empty inputs, invalid parameters
4. **Regression tests** for bug fixes (test the specific bug)

**Run tests before committing:**

.. code-block:: bash

   # Run all tests
   uv run --group test pytest

   # Run only your changed test files
   uv run --group test pytest tests/grids/test_pillar_grid.py -v

   # Run with coverage
   uv run --group test pytest --cov=petres tests/

**Test file example for a bug fix:**

.. code-block:: python

   # tests/grids/test_pillar_grid.py

   def test_regression_pillar_grid_shape_validation():
       """Regression: Grid shape mismatch with non-square regions.

       Issue: https://github.com/jamalbaylit/petres/issues/42
       """
       # Before fix, this would raise ValueError incorrectly
       vertices = np.array([[0, 0], [10, 0], [10, 5], [0, 5]])
       grid = PillarGrid(vertices, n_layers=2)
       assert grid.shape == (10, 5, 2)

Documentation
-------------

All public APIs need docstrings. Ensure:

- Public function/class has a docstring in Google style
- Docstring includes ``Args``, ``Returns``, ``Raises`` sections
- Docstrings include runnable examples (if user-facing)
- Examples are concise and don't require external files

**For new modules/subpackages:**

1. Add module docstring at top of ``.py`` file
2. Update `docs/source/api/` to include new module
3. Build docs locally and verify: ``uv run --group docs sphinx-build -b html docs/source docs/build/html``

Committing Changes
------------------

**Write clear commit messages:**

Format: ``<Type>: <Subject> (<Issue #>)``

Examples:

.. code-block:: bash

   Fix: Grid shape validation for rectangular regions (#42)
   Feature: Add Universal Kriging interpolator (#35)
   Docs: Clarify horizon sampling example (#88)
   Test: Add regression test for ACTNUM broadcast shape

**Guidelines:**

- Keep subject line ≤50 characters
- Use imperative mood: "Fix" not "Fixes" or "Fixed"
- Reference issue number if applicable
- Use multiple commits for logical chunks (don't squash prematurely)

**Example multi-commit workflow:**

.. code-block:: bash

   git add src/petres/grids/pillar.py
   git commit -m "Refactor: Simplify pillar validation logic"

   git add tests/grids/test_pillar_grid.py
   git commit -m "Test: Add edge case for non-square grids (#42)"

   git add src/petres/grids/pillar.py
   git commit --amend  # Fix previous commit if needed

Keeping Your Fork Updated
--------------------------

Before opening a PR, sync with the latest upstream:

.. code-block:: bash

   git fetch upstream
   git rebase upstream/dev  # Or main, depending on target branch

If there are merge conflicts, resolve them:

.. code-block:: bash

   # Edit conflicted files, then:
   git add <resolved-files>
   git rebase --continue

Push your changes:

.. code-block:: bash

   git push origin <branch-name> --force-with-lease

Opening a Pull Request
----------------------

**Before submitting:**

1. Code is formatted: ``uv run ruff format src tests docs``
2. Type hints pass: ``uv run mypy src/petres``
3. All tests pass: ``uv run --group test pytest``
4. Docstrings are present and follow Google style
5. Commits are logical and have descriptive messages

**To create a PR:**

1. Push your branch: ``git push origin <branch-name>``
2. Go to https://github.com/jamalbaylit/petres
3. Click "New Pull Request" and select your branch
4. Fill out the PR template (GitHub shows one automatically)

**PR Description Template:**

.. code-block:: markdown

   ## Description
   Brief explanation of changes you made.

   Fixes #<issue-number> (if applicable)

   ## Type of Change
   - [ ] Bug fix (non-breaking change fixing an issue)
   - [ ] New feature (non-breaking addition)
   - [ ] Documentation update
   - [ ] Breaking change (requires major version bump)

   ## How to Test
   Steps to verify the changes work:

   ```bash
   uv run --group test pytest tests/grids/test_pillar_grid.py::test_shape
   ```

   ## Checklist
   - [ ] Tests pass locally
   - [ ] Code formatted with Ruff
   - [ ] Type hints added
   - [ ] Docstrings added/updated
   - [ ] Changelog entry added (if needed)
   - [ ] No breaking changes (or documented)

Pull Request Review Process
---------------------------

**Reviewers will check:**

1. **Code quality** — readability, style consistency, no redundancy
2. **Tests** — coverage, edge cases, integration scenarios
3. **Documentation** — docstrings, examples, clarity
4. **Performance** — no unnecessary computations, efficient algorithms
5. **API design** — public interfaces are intuitive and consistent

**Responding to Reviews:**

- Address all feedback before merging
- Push updates to the same PR branch (no new PR needed)
- Mark conversations as resolved after addressing feedback
- Ask clarifying questions if feedback is unclear

**After approval:**

- Maintainers will merge your PR
- Your branch will be deleted automatically

Changelog
---------

For user-facing changes, add an entry to `CHANGELOG.md`:

**Format:**

.. code-block:: markdown

   ## [Unreleased]

   ### Added
   - New Universal Kriging interpolator with drift support

   ### Fixed
   - Grid shape validation for rectangular (non-square) regions (#42)

   ### Changed
   - IDW interpolator now caches KD-tree for performance

   ### Removed
   - Deprecated `read_grdecl_legacy()` function

See `Keep a Changelog <https://keepachangelog.com/>`_ for format conventions.

Release Process
---------------

*For maintainers only:*

1. Update version in `src/petres/__init__.py`
2. Update CHANGELOG: replace ``[Unreleased]`` with version and date
3. Create a git tag: ``git tag v0.2.0``
4. Push to main: ``git push origin main --tags``
5. GitHub Actions builds and publishes to PyPI automatically

Troubleshooting
---------------

**Tests fail locally but pass in CI**
   - Ensure Python version matches CI (3.11, 3.12, 3.13)
   - Run: ``uv sync --python 3.11 && uv run pytest``
   - Check for OS-specific issues (Windows vs Unix paths)

**Ruff or MyPy fails unpredictably**
   - Clear cache: ``rm -rf .ruff_cache && uv sync --reinstall-package petres``
   - Reinstall tools: ``uv pip install --upgrade ruff mypy``

**Merge conflicts after rebase**
   - Edit conflicted files to resolve differences
   - Run: ``git add <files> && git rebase --continue``
   - If stuck: ``git rebase --abort`` and try again

**How do I run just one test?**
   - ``uv run --group test pytest tests/grids/test_pillar_grid.py::test_shape_validation -v``

**How do I debug a failing test?**
   - Add ``print()`` statements and run: ``uv run --group test pytest -s``
   - Drop into debugger: ``uv run --group test pytest --pdb``

Getting Help
------------

- **Questions**: Open a GitHub Discussion or Issue
- **Bug reports**: Open a GitHub Issue with minimal reproduction
- **Code review**: Review submitted PRs (feedback is welcome from anyone!)
- **Documentation**: Suggest improvements via PR or Issue

Recognition
-----------

All contributors are recognized in:

- ``CONTRIBUTORS.md`` file in the repository
- Release notes for versions they contributed to
- GitHub "Contributors" page (automatic)

We appreciate all contributions, regardless of size!

Next Steps
----------

- Read :doc:`setup` to set up development environment
- Read :doc:`testing` for comprehensive testing guidelines
- Read :doc:`documentation` for docstring standards
- Check recent PRs for examples of merged contributions

Thank you for contributing to Petres! 🚀
