Grid Types in Reservoir Simulation
==================================

Reservoir simulation relies on numerical grids to represent subsurface geometry, rock properties, and fluid flow behavior. 
Understanding **grid types in reservoir simulation** is essential for selecting an appropriate discretization strategy, balancing numerical accuracy, computational efficiency, and geological realism.

This guide explains the main grid classifications used in reservoir simulation, including:

- Structured and unstructured grids
- Grid geometry (Cartesian vs corner-point grids)
- Grid spacing (uniform vs non-uniform)
- Conforming and non-conforming grids

These concepts form the foundation of grid-based modeling workflows used in simulators such as Eclipse, INTERSECT, and other industry-standard tools.

Overview of Grid Types
----------------------

The classification of grids in reservoir simulation can be understood through four key attributes:

1. **Connectivity** → Structured vs Unstructured
2. **Geometry** → Cartesian vs Corner-point
3. **Spacing** → Uniform vs Non-uniform
4. **Conformity** → Conforming vs Non-conforming

.. figure:: _static/images/grid_classification_overview.png
   :align: center
   :width: 80%

   Figure 1: Classification of grid types used in reservoir simulation.

These attributes are independent but often interrelated. For example, most corner-point grids are structured and conforming, while unstructured grids are commonly used for non-conforming and highly complex geometries.

Structured vs Unstructured Grids
--------------------------------

The most fundamental distinction between grid types lies in **connectivity**, which defines how grid cells are indexed and how neighboring relationships are established.

Structured Grids
~~~~~~~~~~~~~~~~

A **structured grid** consists of cells arranged in a logical three-dimensional array indexed by ``(i, j, k)``.

Each grid cell has a fixed set of neighbors:

- ``(i±1, j, k)``
- ``(i, j±1, k)``
- ``(i, j, k±1)``

Key advantages:

- Efficient memory storage using multidimensional arrays
- Fast traversal and indexing
- Straightforward implementation of finite-difference and finite-volume methods

Structured grids are widely used in reservoir simulation because they provide a strong balance between performance and simplicity.

Unstructured Grids
~~~~~~~~~~~~~~~~~~

An **unstructured grid** does not rely on index-based connectivity. Instead:

- Cells are identified by unique IDs
- Neighbor relationships are stored explicitly (adjacency lists)

Key advantages:

- Flexible cell shapes (tetrahedral, polyhedral)
- Local refinement without global constraints
- Better representation of faults, fractures, and complex geology

Trade-offs:

- Increased memory requirements
- Higher computational complexity
- More complex numerical implementation

.. figure:: _static/images/structured_vs_unstructured.png
   :align: center
   :width: 75%

   Figure 2: Comparison of structured and unstructured grid connectivity.

Grid Geometry: Cartesian vs Corner-Point
----------------------------------------

Geometry defines how grid cells are positioned and shaped in physical space.

Cartesian Grids
~~~~~~~~~~~~~~~

A **Cartesian grid** is the simplest structured grid:

- Grid lines are aligned with coordinate axes
- Cells are rectangular (2D) or cuboidal (3D)
- Spacing is uniform in all directions

Cartesian grids are commonly used for:

- Conceptual models
- Early-stage simulations
- Benchmarking studies

However, they are limited in representing realistic geological structures.

Corner-Point Grids
~~~~~~~~~~~~~~~~~~

A **corner-point grid** is the industry standard for reservoir simulation.

Each cell is defined by **eight corner points**, allowing:

- Skewed and non-orthogonal geometries
- Faulted and truncated layers
- Variable thickness and dip

Despite geometric flexibility, corner-point grids remain **structured grids** because connectivity is still defined by ``(i, j, k)`` indexing.

.. figure:: _static/images/corner_point_grid_example.png
   :align: center
   :width: 75%

   Figure 3: Example of a corner-point grid representing complex reservoir geometry.

Corner-point grids are used in simulators such as Eclipse through keywords like:

- ``COORD`` (pillar geometry)
- ``ZCORN`` (corner depths)
- ``ACTNUM`` (active cells)

Grid Spacing: Uniform vs Non-Uniform
------------------------------------

Grid spacing describes how cell sizes vary across the domain.

Uniform Grids
~~~~~~~~~~~~~

In a **uniform grid**:

- Cell dimensions (Δx, Δy, Δz) are constant
- All cells have identical size and shape

Advantages:

- Simple numerical formulation
- Predictable resolution

Non-Uniform Grids
~~~~~~~~~~~~~~~~~

In a **non-uniform grid**:

- Cell sizes vary spatially
- Refinement can be applied locally

Advantages:

- Higher resolution near wells
- Better representation of gradients
- Improved computational efficiency

.. figure:: _static/images/grid_spacing.png
   :align: center
   :width: 70%

   Figure 4: Uniform versus non-uniform grid spacing.

Conforming vs Non-Conforming Grids
----------------------------------

Conformity describes how cell faces connect to neighboring cells.

Conforming Grids
~~~~~~~~~~~~~~~~

In a **conforming grid**:

- Each cell face matches exactly one neighboring face
- Interfaces are geometrically consistent

Advantages:

- Simpler flux calculations
- Easier implementation of conservation laws
- Efficient data structures

Most structured grids (including corner-point grids) are conforming.

Non-Conforming Grids
~~~~~~~~~~~~~~~~~~~~

In a **non-conforming grid**:

- A single face may connect to multiple neighboring faces
- Face partitioning differs across cells

Common in:

- Local grid refinement
- Adaptive mesh refinement (AMR)

Challenges:

- Complex flux calculations
- Additional data structures required
- More advanced numerical handling

.. figure:: _static/images/nonconforming_grid.png
   :align: center
   :width: 75%

   Figure 5: Example of non-conforming grid with partial face matching.

Comparison of Grid Types
------------------------

+----------------------+-------------+-------------------+------------------------------+
| Grid Type            | Structured? | Geometry          | Typical Use                  |
+======================+=============+===================+==============================+
| Cartesian            | Yes         | Orthogonal        | Simple models                |
+----------------------+-------------+-------------------+------------------------------+
| Rectilinear          | Yes         | Orthogonal        | Variable spacing             |
+----------------------+-------------+-------------------+------------------------------+
| Corner-point         | Yes         | Skewed / faulted  | Reservoir simulation         |
+----------------------+-------------+-------------------+------------------------------+
| Unstructured         | No          | Arbitrary         | Complex geology              |
+----------------------+-------------+-------------------+------------------------------+

Practical Considerations
------------------------

In real-world reservoir simulation:

- **Corner-point grids** are the most widely used
- **Structured grids** dominate due to performance advantages
- **Unstructured grids** are preferred for highly complex reservoirs
- **Non-uniform spacing** is essential for efficient resolution control

The choice of grid type directly impacts:

- Simulation accuracy
- Computational cost
- Numerical stability

FAQ
---

What grid type is most common in reservoir simulation?
   Corner-point grids are the most widely used because they balance structured indexing with geometric flexibility.

What is the difference between structured and unstructured grids?
   Structured grids use index-based connectivity, while unstructured grids store connectivity explicitly and allow arbitrary cell shapes.

Is a corner-point grid structured or unstructured?
   A corner-point grid is a structured grid, even though its geometry may be complex and non-orthogonal.

Why are non-uniform grids used?
   Non-uniform grids allow local refinement near wells and regions of interest, improving accuracy without excessive computational cost.