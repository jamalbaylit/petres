.. _horizon-modeling:

Horizon Modeling
================

This tutorial introduces horizon modeling in Petres and demonstrates how to define and visualize horizons.

A horizon represents a continuous subsurface surface defined as
:math:`z = f(x, y)`, where depth or elevation varies spatially across
the model domain. In Petres, horizons are created from sampled
:math:`(x, y, z)` data and reconstructed using an interpolation method.

Overview
--------

A :class:`~petres.models.Horizon` is defined by:

- ``name``: Horizon name
- ``xy``: Spatial coordinates of the input points
- ``z``: Depth or elevation values at those points
- ``interpolator``: Interpolation method used to reconstruct the surface

Once defined, the horizon behaves as a continuous surface and can be
sampled or visualized over any desired grid.

.. important::

   A horizon is a **continuous surface**, not a grid.
   It is evaluated on demand using an interpolator and does not
   contain any inherent discretization.


Creating a Horizon
------------------

The following example creates a horizon from four sample points using
Inverse Distance Weighting (IDW) interpolation.

.. code-block:: python

   import numpy as np

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon

   horizon1 = Horizon(
      name="H1",
      xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
      z=[0, 1, 0, 1],
      interpolator=IDWInterpolator(),
   )


.. note::

   The choice of interpolator directly affects the geometry of the surface.
   See :doc:`/tutorials/interpolators` for more details and additional options.


Creating Additional Horizons
----------------------------

In practical workflows, multiple horizons are typically defined to
represent different structural or stratigraphic surfaces.

.. code-block:: python

   horizon2 = Horizon(
      name="H2",
      xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
      z=[2, 2, 3, 3],
      interpolator=IDWInterpolator(),
   )

   horizon3 = Horizon(
       name="H3",
       xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
       z=[5, 7, 8, 4],
       interpolator=IDWInterpolator(),
   )


Visualizing a Horizon
---------------------

A horizon is continuous, so it must be sampled on a discrete set of
points for visualization.

Petres supports multiple ways to define the sampling grid.


Direct Coordinate Sampling
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide ``x`` and ``y`` coordinates directly:

.. code-block:: python

   horizon1.show(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
   )


Sampling with Limits and Resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   horizon1.show(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )


Sampling with Grid Spacing
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   horizon1.show(
       xlim=(0, 100),
       ylim=(0, 100),
       dx=2,
       dy=2,
   )


.. note::

   These approaches differ only in how the sampling grid is defined.
   The resulting surface is still evaluated from the same interpolated
   horizon model.


Visualizing Multiple Horizons
-----------------------------

Multiple horizons can be displayed together using
:class:`~petres.viewers.Viewer3D`.

.. code-block:: python

   from petres.viewers import Viewer3D

   viewer = Viewer3D()
   viewer.add_horizons(
       horizons=[horizon1, horizon2, horizon3],
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       cmap="viridis",
   )
   viewer.show()


Manual Color Assignment
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   viewer = Viewer3D()

   viewer.add_horizon(
       horizon1,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       color="red",
   )

   viewer.add_horizon(
       horizon2,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       color="blue",
   )

   viewer.add_horizon(
       horizon3,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       color="green",
   )

   viewer.show()


.. important::

   Horizons are reusable objects and can be used:

   - to define multiple zones
   - to construct grids
   - to evaluate depth at arbitrary locations

   They form the structural backbone of the model.


Expected Output
---------------

- An interactive 3D visualization window
- One or more interpolated surfaces
- Geometry consistent with input data and interpolation method


Summary
-------

- Horizons represent continuous surfaces :math:`z = f(x, y)`
- They are defined from scattered data and interpolated
- They are reusable across multiple modeling workflows


Next Steps
----------

- :ref:`zone-modeling`
- :ref:`grid-from-zones-tutorial`