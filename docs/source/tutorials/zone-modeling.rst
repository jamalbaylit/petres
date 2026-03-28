.. _zone-modeling:

Zone Modeling
=============

This tutorial introduces **zone modeling** in Petres.

A zone represents the interval between two horizons and forms a
fundamental building block for stratigraphic and grid-based subsurface
modeling workflows. In Petres, a zone is always defined by a **top**
horizon and a **base** horizon.

This tutorial covers:

- defining a zone from two horizons
- dividing a zone into layers
- visualizing zones using different sampling strategies
- rendering multiple zones in the same 3D view


Overview
--------

A :class:`~petres.models.Zone` represents the space between two
continuous surfaces:

- ``top``: the upper horizon
- ``base``: the lower horizon

Once defined, the zone can be:

- visualized as a geological interval
- subdivided vertically into layers
- used to generate structured corner-point grids


Defining the Bounding Horizons
------------------------------

Before creating a zone, the bounding horizons must be defined.

.. code-block:: python

   import numpy as np

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon, Zone

   horizon1 = Horizon(
       name="H1",
       xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
       z=[0, 1, 0, 1],
       interpolator=IDWInterpolator(),
   )

   horizon2 = Horizon(
       name="H2",
       xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
       z=[2, 2, 3, 3],
       interpolator=IDWInterpolator(),
   )


Creating a Zone
---------------

A zone is defined by assigning top and base horizons:

.. code-block:: python

   zone1 = Zone(name="Z1", top=horizon1, base=horizon2)

.. note::

   In Petres, a zone is always defined between two horizons. It cannot
   exist independently of its bounding surfaces.


Dividing a Zone into Layers
---------------------------

Zones can be subdivided into multiple layers to control vertical
resolution in later modeling workflows.

Petres provides several approaches for defining zone layering.


Uniform Layering
^^^^^^^^^^^^^^^^

Divide the zone into an equal number of layers:

.. code-block:: python

   zone1.divide(nk=4)

This creates **4 layers of equal thickness** between the top and base
horizons.


Layering with Relative Fractions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Layer thicknesses can also be defined proportionally:

.. code-block:: python

   zone1.divide(fractions=[1, 1, 2])

Interpretation:

- the total thickness is divided proportionally
- the first layer receives 1 part
- the second layer receives 1 part
- the third layer receives 2 parts

As a result:

- the first two layers have equal thickness
- the third layer is twice as thick as each of the first two


Layering with Explicit Levels
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Layer boundaries can also be defined directly using normalized levels:

.. code-block:: python

   zone1.divide(levels=[0.0, 0.2, 1.0])

Interpretation:

- ``0.0`` corresponds to the top horizon
- ``1.0`` corresponds to the base horizon
- intermediate values define internal boundaries

This creates:

- a first layer occupying 20% of the total zone thickness
- a second layer occupying the remaining 80%

.. note::

   - ``nk`` is the simplest approach for uniform layering
   - ``fractions`` is useful for proportional thickness control
   - ``levels`` provides direct control over internal boundaries

   Internally, these approaches define normalized positions between
   the top and base horizons.


.. important::

   Layering is applied **per zone** and directly controls the vertical
   discretization of the final corner-point grid.
   
Visualizing a Zone
------------------

Like horizons, zones are continuous and must be sampled for visualization.

Direct Coordinate Sampling
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can provide ``x`` and ``y`` coordinates directly:

.. code-block:: python

   zone1.show(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
   )


Sampling with Limits and Resolution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   zone1.show(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )


Sampling with Grid Spacing
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   zone1.show(
       xlim=(0, 100),
       ylim=(0, 100),
       dx=2,
       dy=2,
   )

.. note::

   These methods differ only in the way the sampling grid is specified.


Visualizing Multiple Zones
--------------------------

Multiple zones can be visualized together using
:class:`~petres.viewers.Viewer3D`.

First, define an additional horizon and zone:

.. code-block:: python

   horizon3 = Horizon(
       name="H3",
       xy=[[0, 0], [100, 0], [100, 100], [0, 100]],
       z=[5, 7, 8, 4],
       interpolator=IDWInterpolator(),
   )

   zone2 = Zone(name="Zone 2", top=horizon2, base=horizon3)


Using a Colormap
^^^^^^^^^^^^^^^^

.. code-block:: python

   from petres.viewers import Viewer3D

   viewer = Viewer3D()
   viewer.add_zones(
       zones=[zone1, zone2],
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       cmap="viridis",
   )
   viewer.show()

This applies colors automatically using the selected colormap.


Manual Color Assignment
^^^^^^^^^^^^^^^^^^^^^^^

You can also assign colors explicitly:

.. code-block:: python

   viewer = Viewer3D()

   viewer.add_zone(
       zone1,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       color="red",
   )

   viewer.add_zone(
       zone2,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       color="blue",
   )

   viewer.show()


Expected Output
---------------

After running this tutorial, you should see:

- an interactive 3D visualization window
- one or more zones rendered between their bounding horizons
- geometry that follows the interpolated top and base surfaces
- either automatic or manually assigned colors
- layered vertical structure when zone division is used in later workflows


Summary
-------

In this tutorial, you learned how to:

- define a zone from two horizons
- divide a zone into layers using different methods
- visualize a zone using multiple sampling strategies
- render multiple zones in a single 3D viewer

