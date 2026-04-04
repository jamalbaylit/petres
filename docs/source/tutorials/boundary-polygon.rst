Boundary Polygon
================

A boundary polygon allows you to define an arbitrary 2D region on your grid. Cells outside this region can be inactivated using the :meth:`~petres.grids.CornerPointGrid.apply_boundary` method.

Creating a Boundary Polygon
---------------------------

You can create a boundary polygon either by specifying its vertices or by defining a bounding box.


Using Vertices
~~~~~~~~~~~~~~

Boundary polygons can be defined by specifying the vertices of the polygon in :math:`(x, y)` coordinates.

.. code-block:: python

    from petres.models.boundary import BoundaryPolygon

    boundary = BoundaryPolygon(
        name="Boundary", 
        vertices=[[0, 0], [1, 5], [2, 1], [1, 1]]
    )

    # Visualize the polygon in 2D
    boundary.show()

Here, the ``vertices`` parameter defines the coordinates of the polygon corners. The ``name`` parameter is optional and can be used to label the polygon.  
The :meth:`~petres.models.BoundaryPolygon.show` method visualizes the polygon in 2D space.

Using a Bounding Box
~~~~~~~~~~~~~~~~~~~~

You can also create a rectangular polygon using the :meth:`~petres.models.BoundaryPolygon.from_bbox` class method:

.. code-block:: python

    boundary = BoundaryPolygon.from_bbox(
        xmin=0, ymin=0, xmax=1, ymax=5,
        name="Boundary"
    )
    boundary.show()

Applying the Boundary to a Grid
-------------------------------

Once the boundary polygon is defined, you can apply it to a :class:`~petres.grids.CornerPointGrid` to inactivate cells outside the polygon.

.. code-block:: python

    from petres.models.grid import CornerPointGrid

    # Load grid from a grdecl file
    grid = CornerPointGrid.from_grdecl("path_to_file.GRDECL")
    grid.show()

    # Apply the boundary polygon to inactivate out-of-boundary cells
    grid.apply_boundary(boundary)
    grid.show()

.. note::

    The :meth:`~petres.grids.CornerPointGrid.apply_boundary` method does not ignore the existing inactive cells of the grid.  
    It acts as an additional mask on top of the existing active cells.