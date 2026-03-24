Grid Classification
===================

Reservoir simulation grids can be classified based on how cells are
organized, connected, and discretized in space. These classifications
define both the numerical behavior of the grid and its suitability for
representing geological complexity.

Structured vs Unstructured Grids
--------------------------------

The most fundamental distinction lies in how grid cells are indexed
and connected.

A **structured grid** arranges cells in a logical three-dimensional array,
where each cell is uniquely identified by indices ``(i, j, k)``.

Neighbor relationships are implicit through index adjacency:

- ``(i±1, j, k)``
- ``(i, j±1, k)``
- ``(i, j, k±1)``

This regular topology enables:

- Efficient memory layout using arrays  
- Fast grid traversal  
- Simple implementation of finite-difference schemes  

An **unstructured grid**, by contrast, does not rely on ordered indexing.

- Cells are identified by unique IDs  
- Connectivity is stored explicitly (e.g., adjacency lists)  

This provides:

- Flexible representation of complex geometries  
- Support for arbitrary polyhedral cells  
- Localized mesh refinement  

However, this comes at the cost of:

- Higher memory requirements  
- Increased computational complexity  

Uniform vs Non-Uniform Grids
----------------------------

Grid spacing describes how cell dimensions vary across the domain.

In a **uniform grid**, spacing is constant:

- ``Δx``, ``Δy``, ``Δz`` remain fixed  
- All cells have identical dimensions  

In a **non-uniform grid**, spacing varies spatially:

- Cell sizes change along one or more directions  

This allows:

- Local grid refinement  
- Higher resolution near wells or boundaries  

Conforming vs Non-Conforming Grids
----------------------------------

Grid conformity defines how cell faces align between neighboring cells.

In a **conforming grid**:

- Each face matches exactly one neighboring face  
- Cell geometry aligns consistently  

This results in:

- Simpler numerical implementation  
- Efficient data structures  
- Easier parallelization  

Typical examples include:

- Cartesian grids  
- Rectilinear grids  
- Standard corner-point grids  

In a **non-conforming grid**:

- A single face may connect to multiple neighboring faces  
- Face alignment is partial or irregular  

This commonly occurs in:

- Local grid refinement  
- Adaptive mesh refinement (AMR)  

These grids require:

- More complex data structures  
- Advanced flux calculations  
- Careful conservation handling  

.. figure:: _static/images/nonconforming_grid.png
   :align: center
   :width: 70%

   Non-conforming grid example showing mismatched face connectivity.