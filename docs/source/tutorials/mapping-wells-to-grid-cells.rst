Mapping Wells to Grid Cells
===========================

This method maps a vertical well to the grid column it intersects 
based on the top surface geometry. Active or inactive cells are 
ignored. If the well lies outside the grid, the method returns ``None``.

.. code-block:: python

    from petres.models import VerticalWell

    well = VerticalWell("Well-A", x=100, y=200)
    i, j = grid.well_indices(well)

    # Or using (x, y) coordinates directly
    i, j = grid.well_indices((100, 200))

You can pass either a :class:`~petres.models.VerticalWell` object or an ``(x, y)`` tuple.
The returned ``(i, j)`` are zero-based grid indices. ``i`` is the x-direction index,
``j`` is the y-direction index, and both start from 0.