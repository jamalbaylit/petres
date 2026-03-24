Grid Classification
===================

Reservoir simulation grids are broadly classified based on how
cells are connected and indexed.

Grid Connectivity: Structured and Unstructured Grids
----------------------------------------------------



The most fundamental distinction between grid types lies in their connectivity—how grid blocks are indexed and interconnected throughout the grid.

A **structured grid** is characterized by grid blocks arranged in a logical three-dimensional array, where each grid block can be uniquely addressed by a triplet of indices ``(i, j, k)`` corresponding to spatial directions.

Neighbor connectivity is implicitly defined through index adjacency:

- ``(i±1, j, k)``
- ``(i, j±1, k)``
- ``(i, j, k±1)``

This regular topology enables:

- Efficient data storage using array structures
- Fast traversal algorithms
- Straightforward finite-difference implementations

An **unstructured grid**, by contrast:

- Uses unique cell IDs instead of ordered indices
- Stores connectivity explicitly (adjacency lists / tables)

Advantages:

- Arbitrary polyhedral cells
- Local refinement flexibility
- Better representation of faults and complex geology

Trade-offs:

- Higher memory usage
- Increased computational complexity





Uniform (Equidistant) vs Non-Uniform Grids
------------------------------------------

Grid spacing describes the variation of cell dimensions.

Uniform Grids
-------------

In a **uniform grid**:

- Δx, Δy, Δz are constant along each axis
- All cells have identical sizes

Non-Uniform Grids
-----------------

In a **non-uniform grid**:

- Spacing varies along one or more directions
- Cell sizes change spatially

This allows:

- Local refinement
- Better resolution near wells or boundaries








Grid Conformity: Conforming vs Non-Conforming Grids
---------------------------------------------------

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