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

You can find a full list of available grid attributes in the :ref:`<grid-attributes>` section.

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