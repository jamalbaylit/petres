.. _horizon-modeling:

Horizon Modeling
================

This tutorial covers horizon modeling in Petres, including how to define,
reconstruct, and visualize continuous subsurface surfaces.


Overview
--------

A horizon is a continuous subsurface surface defined as
:math:`z = f(x, y)`, where the value represents depth or elevation
across the model domain.

In Petres, horizons are constructed from sampled :math:`(x, y, z)` data
using the :class:`~petres.models.Horizon` class and reconstructed via
interpolation. Once defined, the surface can be evaluated at any
location and visualized over arbitrary grids.

.. important::

   A horizon is a **continuous surface**, not a grid.
   It is evaluated on demand using an interpolator and does not
   contain inherent discretization.

Creating a Horizon
------------------

The following example creates a horizon from four sample points using
Inverse Distance Weighting (IDW) interpolation.

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon

   horizon1 = Horizon(
      name="H1",
      xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
      depth=[0, 1, 0, 1],
      interpolator=IDWInterpolator(),
   )

Here, ``name`` defines the name of horizon, 
``xy`` specifies the spatial coordinates of the sample points,
``depth`` provides their corresponding depth (or elevation) values,
and interpolator controls how the continuous surface is reconstructed from these data.

.. note::

   The choice of interpolator directly affects the geometry of the surface.
   See :doc:`/tutorials/interpolators` for more details and additional options.


Visualizing a Horizon
---------------------

A horizon is mathematically a continuous surface. However, it is not
possible to represent or visualize a truly continuous function on a
computer, since numerical data must be stored at a finite number of points.
Therefore, the surface is sampled on a discrete set of points for
visualization.

Petres provides multiple ways to define this sampling grid.

Direct Coordinate Sampling
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide ``x`` and ``y`` coordinates defining the spatial sampling grid of the horizon surface:

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


Next Steps
----------

- :ref:`zone-modeling`
- :ref:`grid-modeling-from-horizons-and-zones`