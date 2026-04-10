.. _horizon-modeling:

Horizon Modeling
================

A horizon is a continuous subsurface surface defined as
:math:`z = f(x, y)`, where the value represents depth or elevation
across the model domain.

In Petres, horizons are constructed from sampled :math:`(x, y, z)` data
using the :class:`~petres.models.Horizon` class and reconstructed via
interpolation. Once defined, the surface can be evaluated at any
location and visualized over arbitrary grids.

.. note::

   A horizon is a **continuous surface**, not a grid.
   It is evaluated on demand using an interpolator and does not
   contain inherent discretization.

Creating a Horizon
------------------

Horizons in Petres can be created in two ways: **from sample points** or **from well tops**.

.. _horizon-from-points:

From Sample Points
~~~~~~~~~~~~~~~~~~

You can define a horizon directly from smaple points using an interpolator.
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

   The choice of interpolator affects the geometry of the surface.  
   See :doc:`/tutorials/interpolators` page for more details and available options.

.. _horizon-from-wells:

From Well Tops
~~~~~~~~~~~~~~

Horizons can also be generated from well data. When creating a well, you can optionally define **tops** where it intersects horizons:

.. code-block:: python

   from petres.models import VerticalWell

   well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
   well2 = VerticalWell(name="Well 2", x=20, y=78, tops={"Horizon 1": 110})
   well3 = VerticalWell(name="Well 3", x=32, y=55, tops={"Horizon 1": 90})

Here, ``name`` is the well's identifier,
``x`` and ``y`` define its location,
and ``tops`` is a dictionary where the keys are
horizon names and the values are the corresponding depth at that well. 
Multiple horizons can be defined in the same dictionary. 
Tops can also be added after well creation using the :meth:`add_top` method:

.. code-block:: python

   well1.add_top("Horizon 2", 100)
   well2.add_top("Horizon 2", 110)
   well3.add_top("Horizon 2", 90)

Where the first argument is the horizon name and the second is the depth value.

.. note::

   Horizon names must be unique. Reusing an existing name will raise an error.  

Once wells are ready, create a horizon using their tops:

.. code-block:: python

   horizon = Horizon.from_wells(
      name="Horizon 1",
      wells=[well1, well2, well3],
      interpolator=IDWInterpolator()
   )

.. note::

   Wells must have a top defined for the same horizon name; otherwise, horizon creation will fail.

After the horizon is created, you can find the depth where it intersects **any well**, even if the well was not used for interpolation:

.. code-block:: python

   print(horizon.intersect(well2))


.. _horizon-visualization:

Visualizing a Horizon
---------------------

Once a horizon has been defined in Petres, it can be quickly visualized using the
:meth:`show` method. This provides an immediate view of the horizon surface, helping
to inspect its shape. 

Horizon surfaces are mathematically continuous, defined as :math:`z = f(x, y)`.
However, computers can only represent a finite number of points. To visualize a
horizon, the continuous surface is therefore sampled on a discrete grid. Petres
offers multiple ways to define this sampling grid.

Direct Coordinate Sampling
~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify the exact :math:`x` and :math:`y` coordinates to define the spatial
sampling grid:

.. code-block:: python

   horizon1.show(
      x=np.linspace(0, 100, 50),
      y=np.linspace(0, 100, 50),
   )

Sampling with Limits and Resolution
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of providing coordinates directly, you can define the grid using limits
and the number of points along each axis:

.. code-block:: python

   horizon1.show(
      xlim=(0, 100),
      ylim=(0, 100),
      ni=50,
      nj=50,
   )

Sampling with Grid Spacing
~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can specify the desired spacing between grid points along each
axis:

.. code-block:: python

   horizon1.show(
      xlim=(0, 100),
      ylim=(0, 100),
      dx=2,
      dy=2,
   )

.. note::

   All these approaches differ only in how the sampling grid is defined for visualization purposes.
   The underlying horizon surface is always evaluated using the same interpolated model,
   regardless of how the visualization grid is specified.


By default, :meth:`~petres.models.Horizon.show` renders the horizon surface in 3D. 
However, the ``view`` argument allows switching between 2D and 3D visualizations.
To visualize the horizon in 2D, set ``view="2d"``:

.. code-block:: python

   horizon1.show(
      x=np.linspace(0, 100, 50),
      y=np.linspace(0, 100, 50),
      view="2d"
   )

For more advanced control over the visualization, Petres provides separate
:meth:`~petres.models.Horizon.show2d` and :meth:`~petres.models.Horizon.show3d` methods,
which offer additional customization options for 2D and 3D plots, respectively. 

Wells can also be visualized alongside horizons by passing them to the ``wells`` argument:

.. code-block:: python

   horizon1.show(
      x=np.linspace(0, 100, 50),
      y=np.linspace(0, 100, 50),
      wells=[well1, well2, well3]
   )


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

.. note::

   The same grid sampling options described previously for :meth:`~petres.models.Horizon.show` are available here.

Manual Color Assignment
~~~~~~~~~~~~~~~~~~~~~~~

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

   Horizons are reusable objects and can be used to define multiple zones (see :ref:`create-zone-from-horizons`).


Next Steps
----------

- :ref:`zone-modeling`
- :doc:`grid-modeling-from-horizons-and-zones`