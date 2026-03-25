Structured Grid Types
========================

This section presents a subset of structured grid types supported in
**Petres**, namely **Rectilinear**, **Regular**, and **Cartesian** grids.

These grid types share the same structured indexing system, but differ
in how spacing is defined along each coordinate direction. 
They form a hierarchy of increasing geometric constraint,
with Cartesian grids representing the most restrictive case (Cartesian ⊂ Regular ⊂ Rectilinear).
These grid types are illustrated in :numref:`fig-structured-grid-hierarchy`.

.. _fig-structured-grid-hierarchy:
.. figure:: ../_static/fundamentals/cartesian-regular-rectilinear-grid.svg
   :align: center
   :width: 70%
   :class: adaptive-theme-svg

   Illustration of Rectilinear, Regular, and Cartesian grid types.


.. _rectilinear-grids:
Rectilinear Grid
----------------

A **Rectilinear grid** is the most general form within this family of
structured grids. Grid lines are straight and mutually orthogonal,
resulting in rectangular (2D) or cuboidal (3D) grid cells.

Grid spacing may vary independently along each coordinate direction:

.. math::
   \Delta x = \Delta x(i), \quad \Delta y = \Delta y(j), \quad \Delta z = \Delta z(k)

This allows non-uniform discretization, enabling local grid refinement
in regions of interest while preserving a structured topology.

.. _regular-grids:
Regular Grid
------------

A **Regular grid** is a constrained form of a Rectilinear grid in which
grid spacing is constant along each individual coordinate direction:

.. math::
   \Delta x = \text{const}, \quad \Delta y = \text{const}, \quad \Delta z = \text{const}

However, spacing may differ between directions (i.e., :math:`\Delta x \neq \Delta y \neq \Delta z`).
As a result, all grid cells have identical dimensions within each axis,
but are not necessarily isotropic. Cells are rectangular prisms in 3D,
with consistent geometry throughout the domain. 
This structure simplifies numerical implementation while still allowing
anisotropic resolution.

.. _cartesian-grids:
Cartesian Grid
--------------

A **Cartesian grid** represents the most restrictive case within this
hierarchy. Grid spacing is uniform and isotropic in all directions:

.. math::
   \Delta x = \Delta y = \Delta z = \text{const}

All cells are geometrically identical, forming squares in 2D and cubes
in 3D. This configuration provides:

- Maximum simplicity in grid generation
- Optimal memory layout and computational efficiency
- Straightforward implementation of finite-difference schemes

However, it lacks flexibility for representing geometric complexity or
localized refinement without increasing global resolution.
