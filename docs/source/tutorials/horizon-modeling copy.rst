.. _tutorial-horizons:

Horizon Modeling
================

This tutorial demonstrates how to construct, manipulate, and visualize
**horizons** in Petres.

A *Horizon* represents a continuous subsurface surface:

.. math::

   z = f(x, y)

It is defined from discrete depth picks and an interpolation method,
commonly derived from seismic interpretation or well tops.

---

Overview
--------

In this tutorial, you will learn how to:

- Create a Horizon from scattered picks
- Build a Horizon from well tops
- Modify well tops
- Evaluate horizon–well intersections
- Visualize horizons using different sampling strategies
- Display multiple horizons in a 3D scene

---

Creating a Horizon from Scattered Picks
---------------------------------------

A Horizon can be constructed directly from discrete ``(x, y, z)`` points
using an interpolator.

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon
   import numpy as np

   horizon = Horizon(
       name="H1",
       xy=[[20, 78], [55, 65], [90, 35.5]],
       z=[100, 110, 90],
       interpolator=IDWInterpolator(),
   )

   horizon.show(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
   )

**Notes**

- The interpolator defines how the surface is reconstructed between points.
- Any compatible interpolator can be used (see :ref:`interpolators`).

---

Creating a Horizon from Well Tops
---------------------------------

In many workflows, horizons are derived from well tops rather than
manually defined points.

.. code-block:: python

   from petres.models import VerticalWell

   well1 = VerticalWell(name="Well 1", x=20, y=78, tops={"Horizon 1": 100})
   well2 = VerticalWell(name="Well 2", x=55, y=65, tops={"Horizon 1": 110})
   well3 = VerticalWell(name="Well 3", x=90, y=35.5, tops={"Horizon 1": 90})

Additional tops can be assigned after well creation:

.. code-block:: python

   well1.add_top(horizon="Horizon 2", depth=140)
   well2.add_top(horizon="Horizon 2", depth=125)
   well3.add_top(horizon="Horizon 2", depth=110)

A Horizon can then be constructed from wells that contain the required
top:

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon

   horizon = Horizon.from_wells(
       name="Horizon 1",
       wells=[well1, well2, well3],
       interpolator=IDWInterpolator(),
   )

   horizon.show(
       x=np.linspace(0, 100, 100),
       y=np.linspace(0, 100, 100),
   )

---

Well–Horizon Intersection
-------------------------

The depth at which a horizon intersects a well can be evaluated directly:

.. code-block:: python

   print(horizon.intersect(well2))

The well does not need to be used during horizon construction.

---

Updating Well Tops
------------------

A horizon top cannot be added again if it already exists in a well.
To update a value, remove the existing top first:

.. code-block:: python

   well2.remove_top("Horizon 1")
   well2.add_top("Horizon 1", 120)

---

Horizon Visualization
---------------------

Since horizons are continuous surfaces, they must be sampled on a discrete
set of points for visualization.

**Option 1 — Explicit sampling**

.. code-block:: python

   horizon.show(
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
   )

**Option 2 — Domain limits with resolution**

.. code-block:: python

   horizon.show(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )

**Option 3 — Domain limits with spacing**

.. code-block:: python

   horizon.show(
       xlim=(0, 100),
       ylim=(0, 100),
       dx=2,
       dy=2,
   )

---

Visualizing Multiple Horizons
-----------------------------

Multiple horizons can be displayed in a single 3D scene.

.. code-block:: python

   from petres.viewers import Viewer3D
   import numpy as np

   horizon2 = Horizon.from_wells(
       name="Horizon 2",
       wells=[well1, well2, well3],
       interpolator=IDWInterpolator(),
   )

   viewer = Viewer3D()

   viewer.add_horizons(
       horizons=[horizon, horizon2],
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       cmap="viridis",
   )

   viewer.show()

Alternatively, horizons can be added individually with explicit colors:

.. code-block:: python

   viewer = Viewer3D()

   viewer.add_horizon(
       horizon,
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

   viewer.show()

---

Summary
-------

In this tutorial, you have:

- Constructed horizons from scattered data and well tops
- Managed well top data
- Evaluated horizon intersections
- Explored multiple visualization approaches
- Rendered multiple horizons in a shared 3D environment

---

Next Steps
----------

- :ref:`tutorial-zones` — Build zones between horizons
- :ref:`corner-point-grids` — Generate grids from geological models
- :ref:`properties` — Assign and visualize reservoir properties