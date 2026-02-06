.. petromod documentation master file

petromod Documentation
======================

**petromod** is a Python library for petroleum and reservoir modeling.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   api/index

Getting Started
---------------

Install the package using pip:

.. code-block:: bash

   pip install petromod

Quick Example
-------------

.. code-block:: python

   from petromod.grids import Rectilinear2DGrid
   import numpy as np

   # Create a simple grid
   x = np.linspace(0, 100, 11)
   y = np.linspace(0, 50, 6)
   active = np.ones((5, 10), dtype=bool)
   
   grid = Rectilinear2DGrid(x, y, active)
   print(f"Grid shape: {grid.cell_shape}")

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
