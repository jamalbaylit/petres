Boundary Polygon
================

This tutorial demonstrates how to define a boundary polygon and apply it to a grid in Petres to inactivate cells that lie outside the polygon.

Overview
--------

A **boundary polygon** allows you to define an arbitrary 2D region on your grid. Cells outside this region can be inactivated using the `apply_boundary` method of a `CornerPointGrid`.

Creating a Boundary Polygon
---------------------------

Boundary polygons can be defined by specifying the vertices of the polygon in (x, y) coordinates.

Example:

.. code-block:: python

    from petres.models.boundary import BoundaryPolygon
    import numpy as np

    # Define a boundary polygon with custom vertices
    boundary = BoundaryPolygon(
        name="Boundary", 
        vertices=[[0, 0], [1, 5], [2, 1], [1, 1]]
    )

    # Visualize the polygon in 2D
    boundary.show()

In this example, the `vertices` parameter defines the coordinates of the polygon corners. The `name` parameter is optional and can be used to label the polygon.

Creating a Polygon from a Bounding Box
--------------------------------------

You can also create a rectangular polygon using the `from_bbox` class method:

.. code-block:: python

    boundary = BoundaryPolygon.from_bbox(
        xmin=0, ymin=0, xmax=1, ymax=5,
        name="Boundary"
    )
    boundary.show()

Applying the Boundary to a Grid
-------------------------------

Once the boundary polygon is defined, you can apply it to a `CornerPointGrid` to inactivate cells outside the polygon.

.. code-block:: python

    from petres.models.grid import CornerPointGrid

    # Load grid from a grdecl file
    grid = CornerPointGrid.from_grdecl("path_to_grdecl_file", use_actnum=True)
    grid.show()

    # Apply the boundary polygon to inactivate out-of-boundary cells
    grid.apply_boundary(boundary)
    grid.show()

Notes
-----

- The `apply_boundary` method modifies the grid `actnum` array to inactivate cells outside the polygon.
- Multiple boundaries can be defined and applied sequentially if needed.
- Visualization of the boundary with `show()` helps ensure the polygon matches the intended region.

Summary
-------

Using `BoundaryPolygon` in Petres allows precise control over which cells are active within a grid. You can define polygons manually via vertices or quickly generate rectangular boundaries using `from_bbox`. Applying the boundary ensures that grid operations and simulations consider only the cells within the defined region.
