.. _zone-modeling:

Zone Modeling
=============

A zone in Petres is defined by two horizons, 
where the volume enclosed between them forms the zone. 
Once defined using :class:`~petres.models.Zone`, it can be:

- Visualized in 2D/3D space
- Subdivided into vertical layers
- Used to generate Corner-Point grids


.. _create-zone-from-horizons:

Creating a Zone
---------------

In Petres, a zone can be created in two ways:

- From two horizons
- From a single horizon with a specified thickness


Using Two Horizons
~~~~~~~~~~~~~~~~~~

A zone can be defined explicitly by providing top and base horizons:

.. code-block:: python

   zone1 = Zone(name="Z1", top=horizon1, base=horizon2)

Here, ``horizon1`` and ``horizon2`` are previously defined :class:`~petres.models.Horizon`  
objects representing the upper and lower bounding surfaces, respectively.

Using a Single Horizon
~~~~~~~~~~~~~~~~~~~~~~

Alternatively, a zone can be created from a single horizon by specifying a constant thickness:

.. code-block:: python

   zone = horizon1.to_zone(name="Zone 1", depth=2)
   zone.show(x=np.linspace(0, 5, 50), y=np.linspace(0, 5, 50))

This method generates a second (base) horizon by 
shifting the original horizon downward by the specified depth,
resulting in a zone with constant thickness.

.. important::

   :meth:`~petres.models.Horizon.to_zone` requires the horizon to retain its picks 
   (``store_picks=True``) to generate the shifted base horizon. This is the default 
   behavior, so no action is needed unless you have explicitly changed it.

Dividing a Zone into Layers
---------------------------

Zones can be subdivided into multiple layers to control vertical
resolution in later modeling workflows.
Petres provides several approaches for defining zone layering.


Uniform Layering
~~~~~~~~~~~~~~~~

Divide the zone into an equal number of layers:

.. code-block:: python

   zone1.divide(nk=4)

This creates 4 layers evenly distributed between the top and base horizons.

Layering with Relative Fractions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Layer thicknesses can also be defined proportionally:

.. code-block:: python

   zone1.divide(fractions=[1, 1, 2])

In this example, the zone is divided into three layers where the 
thickness of each layer is proportional to the corresponding fraction.
As a result, the first two layers have equal thickness, 
and the third layer is twice as thick as each of the first two.  


Layering with Explicit Levels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Layer boundaries can be defined directly using 
normalized levels between the top and base horizons:

.. code-block:: python

   zone1.divide(levels=[0, 0.2, 1])

As a result, the first layer occupies 20% of the total zone thickness, 
and the second layer occupies the remaining 80%. 
Here, `0` corresponds to the top horizon, `1` to the base horizon, 
and intermediate values define internal boundaries.  

.. important::

   Layering is applied **per zone** and directly controls the vertical
   discretization of the final corner-point grid.
   

Visualizing a Zone
------------------

Like horizons, zones are continuous and need to be sampled for visualization.
They can be displayed directly using the :meth:`~petres.models.Zone.show` 
method, or with more control in 2D and 3D using 
:meth:`~petres.models.Zone.show2d` and :meth:`~petres.models.Zone.show3d`, respectively.

The grid sampling options are the same as those described for
:ref:`visualizing horizons <horizon-visualization>`. That is, you can
specify the sampling grid using direct coordinates, limits and resolution, or
grid spacing.

Visualizing Multiple Zones
~~~~~~~~~~~~~~~~~~~~~~~~~~

Multiple zones can be displayed together using :class:`~petres.viewers.Viewer3D`.

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

Manual Color Assignment
~~~~~~~~~~~~~~~~~~~~~~~

Colors can also be assigned explicitly:

.. code-block:: python

   viewer = Viewer3D()
   viewer.add_zone(zone1, x=np.linspace(0, 100, 50), y=np.linspace(0, 100, 50), color="red")
   viewer.add_zone(zone2, x=np.linspace(0, 100, 50), y=np.linspace(0, 100, 50), color="blue")
   viewer.show()

Next Steps
----------

- :doc:`grid-modeling-from-horizons-and-zones`
- :doc:`property-modeling`
