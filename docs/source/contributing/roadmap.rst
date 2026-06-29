Roadmap
=======

This document outlines planned features and areas for future improvement.
The items listed here represent potential directions for the project and are
subject to change based on community feedback and project priorities.

Planned Features
----------------

Rectilinear Grid Support
^^^^^^^^^^^^^^^^^^^^^^^^

Introduce a dedicated :class:`RectilinearGrid` class alongside the existing
:class:`~petres.grids.CornerPointGrid`.

The current :class:`~petres.grids.CornerPointGrid` implementation stores the
geometry required for fully general corner-point grids. While this provides
maximum flexibility, it results in unnecessary memory usage for regular
rectilinear grids. A dedicated implementation would significantly reduce memory
consumption while improving computational performance.

Intersect Export Support
^^^^^^^^^^^^^^^^^^^^^^^^

Extend the export framework to support file formats compatible with the
Intersect simulator.
This would enable Petres to support multiple reservoir simulators through a
consistent export interface.

Additional Interpolation Methods
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Expand the interpolation module with additional algorithms suitable for
different datasets and applications.
This would provide users with greater flexibility when working with geological
and reservoir data of varying characteristics.

Future Improvements
-------------------

Test Suite
^^^^^^^^^^

The current test suite provides a solid foundation but would benefit from
improved organization, broader test coverage, and additional integration tests
to improve long-term maintainability.

Documentation
^^^^^^^^^^^^^

Continue expanding the documentation to include:

- Additional conceptual guides
- More practical examples
- Architecture and design documentation
- Improvements to existing documentation for clarity and completeness

Performance Optimizations
^^^^^^^^^^^^^^^^^^^^^^^^^

Continue identifying opportunities to improve execution performance, reduce
memory usage, and increase scalability for large reservoir models.

