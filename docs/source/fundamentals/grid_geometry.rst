Grid Geometry
=============

Topology alone does not describe how a grid is positioned in physical space.
Geometry determines the shape and orientation of cells.

Cartesian Grids
---------------

The simplest case is a **Cartesian grid**, where:

- Grid lines align with coordinate axes
- Cells are rectangular (2D) or cuboidal (3D)

These grids are always structured and commonly used for:

- Simplified models
- Early-stage studies

Corner-Point Geometry
---------------------

For realistic reservoir models, Cartesian geometry is often insufficient.

Geological layers may be:

- Tilted
- Faulted
- Truncated

To represent this complexity, **corner-point (pillar) grids** are used.

Each cell is defined by its **eight corner points**, allowing:

- Non-orthogonal shapes
- Skewed geometries
- Variable cell sizes

Despite this flexibility, they **remain structured grids**.