Grid Connectivity: Structured and Unstructured Grids
===================================================



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







