Grid Conformity
===============

Conforming vs Non-Conforming Grids
---------------------------------

Conformity describes how cell faces connect to neighboring cells.

Conforming Grids
----------------

In a **conforming grid**:

- Each face matches exactly one neighboring face
- Geometry aligns perfectly

Advantages:

- Simpler numerical implementation
- Efficient data structures
- Easier parallelization

Examples:

- Cartesian grids
- Rectilinear grids
- Standard corner-point grids

Non-Conforming Grids
--------------------

In a **non-conforming grid**:

- One face connects to multiple neighboring faces
- Faces are partially matched

Common in:

- Local refinement
- Adaptive mesh refinement (AMR)

Challenges:

- Complex data structures
- Advanced flux calculations
- Conservation enforcement required

.. figure:: _static/images/nonconforming_grid.png
   :align: center
   :width: 70%

   Figure 1: Example of non-conforming grid with mismatched face connectivity.