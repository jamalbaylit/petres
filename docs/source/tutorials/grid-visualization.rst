Grid Visualization
==================

Petres provides simple and flexible tools to visualize Corner-Point grids in 3D. 

Basic Usage
-----------

You can call the ``show()`` method to display the grid in an interactive 3D viewer:

.. code-block:: python

    from petres.grids import CornerPointGrid

    grid = CornerPointGrid.from_grdecl(
        "path/to/your/grid.GRDECL",
        properties=["PORO", "PERMX"]
    )
    grid.show()


Adjusting Z-Scale
-----------------

You can exaggerate or compress the vertical dimension of the grid using the ``z_scale`` parameter: 

.. code-block:: python

    grid.show(z_scale=3)


``z_scale=1`` represents the default scaling with no change applied, 
while values greater than 1 stretch the grid vertically to enhance 
height differences, and values less than 1 compress the grid vertically.
This is especially useful when your data has small variations in vertical 
axis compared to horizontal axes, making features hard to see.

.. note::
    This only affects visualization and does not modify the original data.

Visualizing Inactive Cells
--------------------------

By default, inactive cells are not displayed. To include them set ``show_inactive`` to ``True``:

.. code-block:: python

    grid.show(show_inactive=True)

Using Built-in Grid Attributes
------------------------------

Petres includes several built-in grid attributes, such as ``top`` and ``active``. These can be used to color the grid:

.. code-block:: python

    grid.show(scalars="top")
    grid.show(scalars="active")

You can find a full list of available grid attributes in the :ref:`grid-attributes` section.

Visualizing Grid Properties
---------------------------

If your grid has imported properties, you can visualize them as scalars:

.. code-block:: python

    # Visualize porosity
    grid.show(scalars="PORO")

    # List all available properties
    print(grid.properties)

Customizing Colors and Titles
-----------------------------

Colors and titles can be customized for better presentation:

.. code-block:: python

    # Using a colormap for scalar visualization
    grid.show(scalars="PORO", cmap="viridis")

    # Using a single color for non-scalar visualization
    grid.show(color="lightblue")

    # Change the plot title
    grid.show(title="Custom Grid Visualization")

.. note::

   For more color options, see the `Matplotlib named colors gallery <https://matplotlib.org/stable/gallery/color/named_colors.html>`_.


Visualizing Wells
-----------------

Petres allows you to visualize vertical wells directly on top of your Corner-Point grid.
Create one or more vertical wells using the :class:`~petres.models.VerticalWell` class and pass them
to the grid’s :meth:`~petres.grids.CornerPointGrid.show` method:

.. code-block:: python

    from petres.grids import CornerPointGrid
    from petres.models import VerticalWell

    grid = CornerPointGrid.from_grdecl("path/to/your/grid.GRDECL")

    # Define wells
    well1 = VerticalWell("Well-1", x=100, y=200)
    well2 = VerticalWell("Well-2", x=120, y=220)

    # Visualize wells on the grid
    grid.show(wells=[well1, well2])

You can also pass a single well directly without wrapping it in a list:

.. code-block:: python

    grid.show(wells=well1)