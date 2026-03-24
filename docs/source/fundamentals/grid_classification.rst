Grid Classification
===================

Reservoir simulation grids can be classified based on how cells are
organized, connected, and discretized in space. These classifications
govern both the numerical behavior of the model and its ability to
represent geological complexity.

Understanding these distinctions is essential when selecting an
appropriate grid for a given reservoir simulation problem.

Structured vs Unstructured Grids
--------------------------------

The most fundamental classification is based on grid connectivity—how
cells are indexed and how neighbor relationships are defined.

In a **structured grid**, cells are arranged in a regular
three-dimensional layout. Each cell is uniquely identified by a triplet
of indices ``(i, j, k)``, which directly encode its spatial position.
Neighboring cells are implicitly defined through index adjacency
(e.g., ``i±1``, ``j±1``, ``k±1``), meaning connectivity does not need to
be stored explicitly.

This regular topology enables efficient memory usage and fast traversal
of grid cells, making structured grids particularly well suited for
finite-difference formulations commonly used in reservoir simulation.

In contrast, an **unstructured grid** does not follow a regular indexing
scheme. Cells are identified by unique IDs, and connectivity must be
stored explicitly using data structures such as adjacency lists.

This flexibility allows unstructured grids to represent complex
geometries more accurately, including faults, irregular boundaries,
and localized refinements. However, this comes at the cost of increased
memory usage and computational complexity.

Uniform vs Non-Uniform Grids
----------------------------

Another important distinction relates to grid spacing, which determines
how cell dimensions vary across the domain.

In a **uniform grid**, spacing remains constant along each axis. The
distances ``Δx``, ``Δy``, and ``Δz`` are fixed, resulting in cells of
identical size throughout the model. This simplicity leads to predictable
numerical behavior and straightforward implementation.

In a **non-uniform grid**, spacing varies spatially, allowing cell sizes
to change along one or more directions. This enables local refinement in
regions of interest, such as near wells, faults, or boundaries, where
higher resolution is required to capture critical flow behavior.

Non-uniform grids therefore provide greater modeling flexibility while
maintaining compatibility with structured grid frameworks.

.. figure:: ../_static/fundamentals/uniform-vs-nonuniform.svg
   :align: center
   :width: 75%
   :class: adaptive-theme-svg

   Uniform vs non-uniform grid spacing comparison.

Conforming vs Non-Conforming Grids
----------------------------------

Grid conformity describes how cell faces align between neighboring cells
and plays an important role in numerical consistency.

.. figure:: ../_static/fundamentals/conforming-vs-nonconforming.svg
   :align: center
   :width: 70%
   :class: adaptive-theme-svg

   Non-conforming grid example showing mismatched face connectivity between adjacent cells.

In a **conforming grid**, each cell face matches exactly one neighboring
face. The geometric alignment between cells is consistent across the
grid, which simplifies flux calculations and supports efficient numerical
schemes. Typical examples include: **Cartesian**, **Rectilinear**, and **Corner-Point** grids.

In a **non-conforming grid**, a single cell face may connect to multiple
neighboring faces, resulting in partial or mismatched alignment. This
situation commonly arises in locally refined grids or adaptive mesh
refinement (AMR) workflows.

While non-conforming grids allow for increased flexibility and targeted
resolution, they require more advanced numerical treatment to ensure
flux consistency and conservation across interfaces.
