Mapping Wells to Grid Cells
===========================

This section shows how to determine which grid cells a well trajectory
intersects and how to retrieve their indices (``i, j, k``) for simulation use.

Input
-----

- Grid model
- Well trajectory as ``(x, y, z)`` coordinates

Output
------

- Ordered list of intersected grid indices:

  ::

      [(i, j, k), ...]

Basic Approach
--------------

1. Loop over well trajectory points
2. Find the containing cell for each point
3. Remove duplicates while preserving order

Example
-------

.. code-block:: python

    indices = []

    for point in well_points:
        idx = grid.find_cell(point)   # returns (i, j, k)
        if idx is not None:
            if not indices or indices[-1] != idx:
                indices.append(idx)

Notes
-----

- This method is fast but may miss cells if trajectory spacing is coarse.
- For better accuracy, check intersections along segments between points.
- The result can be passed directly to simulators as well connections.