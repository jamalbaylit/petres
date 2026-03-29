Property Modeling
=================

Overview
--------

This tutorial introduces property modeling in Petres.
Grid properties are defined per cell and share the same shape as the parent grid.
They represent scalar quantities such as porosity, permeability, saturation,
net-to-gross, or any other spatially distributed field.

In this chapter, you will learn how to:

- Create new grid properties
- Fill them with constant or stochastic values
- Derive one property from another
- Populate values from existing NumPy arrays
- Interpolate property values from wells
- Assign properties zone by zone
- Inspect statistics and summaries
- Visualize the resulting distributions

.. note::

   This tutorial assumes that you are already familiar with
   :doc:`horizon-modeling`,
   :doc:`zone-modeling`,
   :doc:`pillar-gridding`,
   and grid creation workflows such as
   :doc:`grid-modeling-from-horizons-and-zones`.



Creating a Property
-------------------

The first step is to create a property on the grid:

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )

   porosity = grid.properties.create(
       name="poro",
       eclipse_keyword="PORO",
       description="Porosity",
   )

The ``name`` is the internal Petres name used to access the property later.
The optional ``eclipse_keyword`` is useful when exporting the property to
Eclipse ``.GRDECL`` format. The ``description`` is also optional and can be used
to provide a more readable explanation of the property, if needed.

Constant Property Assignment
----------------------------

A property can be filled with a constant value across the whole grid using
:meth:`fill` method:

.. code-block:: python

   porosity.fill(0.2)

This assigns a porosity value of 0.2 to every cell in the property array.

Visualizing a Property
----------------------

A property can be visualized directly.

.. code-block:: python

   porosity.show()

Inactive cells are hidden by default. If needed, they can also be shown:

.. code-block:: python

   porosity.show(show_inactive=True)

A custom Matplotlib colormap may also be supplied:

.. code-block:: python

   porosity.show(cmap="viridis")

Any valid Matplotlib colormap name can be used, such as ``"viridis"``,
``"plasma"``, ``"coolwarm"``, or ``"inferno"``.

Deriving a Property from Another Property
-----------------------------------------

A new property can be computed from one or more existing sources using
:meth:`apply`.
For example, permeability may be derived from porosity:

.. code-block:: python

   permeability = grid.properties.create(
       name="perm",
       eclipse_keyword="PERM",
       description="Permeability",
   )

   permeability.apply(lambda poro: 100 * poro**3, source=porosity)

   permeability.show()

The ``source`` argument may refer to an existing property object, a property name,
or other supported grid-derived variables.

Using Multiple Sources
~~~~~~~~~~~~~~~~~~~~~~

The :meth:`apply` method can also combine multiple sources.

.. code-block:: python

   permeability.apply(
       lambda poro, z: 100 * poro**3 + z,
       source=(porosity, "z"),
   )

   permeability.show()

In this example, permeability is calculated from both porosity and cell depth.

Using a Named Function
~~~~~~~~~~~~~~~~~~~~~~

Instead of a lambda function, you can also provide a regular Python function.

.. code-block:: python

   def calc_perm(poro, z):
       return 100 * poro**3 + z

   permeability.apply(calc_perm, source=(porosity, "z"))

Using a named function is often preferable when the transformation becomes more
complex or needs to be reused.

Property Statistics
-------------------

Petres provides convenient access to common summary statistics.

.. code-block:: python

   print("Min Value:", permeability.min)
   print("Max Value:", permeability.max)
   print("Mean Value:", permeability.mean)
   print("Median Value:", permeability.median)
   print("Standard Deviation:", permeability.std)

You can also print a full summary:

.. code-block:: python

   print(permeability.summary())

This is useful for quickly checking whether the modeled values fall within
reasonable physical limits.

Filling with a Uniform Distribution
-----------------------------------

For stochastic modeling, a property can be filled from a uniform distribution.

.. code-block:: python

   porosity.fill_uniform(low=0.24, high=0.30)
   porosity.show()

This generates values uniformly distributed between the specified lower and upper bounds.

Filling with a Normal Distribution
----------------------------------

A normal distribution can be used when a property is expected to vary around
a representative mean value.

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20 * 4,
       nj=20 * 4,
       nk=3 * 4,
   )

   porosity = grid.properties.create(
       name="poro",
       eclipse_keyword="PORO",
       description="Porosity",
   )

   porosity.fill_normal(mean=0.24, std=0.03)
   porosity.show()

Minimum and maximum clipping bounds may optionally be supplied:

.. code-block:: python

   porosity.fill_normal(mean=0.24, std=0.03, min=0.20, max=0.30)
   porosity.show()

To ensure reproducibility, a random seed may also be set:

.. code-block:: python

   porosity.fill_normal(mean=0.24, std=0.03, seed=42)
   porosity.show()

Filling with a Log-Normal Distribution
--------------------------------------

A log-normal distribution is often more suitable for positively skewed properties,
especially for quantities such as permeability.

.. code-block:: python

   porosity.fill_lognormal(mean=0.24, std=0.03)
   porosity.show()

As with normal filling, optional bounds may be provided:

.. code-block:: python

   porosity.fill_lognormal(mean=0.24, std=0.03, min=0.20, max=0.30)
   porosity.show()

A seed can also be specified for reproducibility:

.. code-block:: python

   porosity.fill_lognormal(mean=0.24, std=0.03, seed=42)
   porosity.show()

Populating a Property from a NumPy Array
----------------------------------------

If you already have a precomputed 3D array of values, it can be assigned directly
to the property.

.. code-block:: python

   import numpy as np

   array = np.full(grid.shape, 0.24)
   porosity.from_array(array)
   porosity.show()

This is especially useful when the property values come from an external workflow,
a simulator output, or a separate numerical calculation.

Zone-Based Property Assignment
------------------------------

If the grid contains zone information, property values can be modeled separately
for each zone.

This is particularly useful when different formations require different property
ranges or modeling assumptions.

The example below assumes that the zones have already been defined, as shown in
earlier tutorials.

.. code-block:: python

   import numpy as np

   zones = [
       Zone("Caprock", top=h1, base=h2).divide(fractions=[0.2, 0.3, 0.5]),
       Zone("Base", top=h3, base=h4).divide(nk=3),
   ]

   viewer.add_zones(
       zones,
       x=np.linspace(0, 100, 50),
       y=np.linspace(0, 100, 50),
       cmap="viridis",
       show_layers=True,
   )
   viewer.show()

   pillars = PillarGrid.from_regular(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )

   grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)
   grid.show(show_inactive=False)

   porosity = grid.properties.create(
       name="poro",
       eclipse_keyword="PORO",
       description="Porosity",
   )

   porosity.fill(0.20, zone="Caprock")
   porosity.fill(0.50, zone="Base")

   porosity.show(show_inactive=False)

The same zone-based idea can be used with other population methods as well,
including ``from_array``, ``fill_uniform``, ``fill_normal``, and
``fill_lognormal``.

For example:

.. code-block:: python

   porosity.fill_normal(mean=0.08, std=0.01, zone="Caprock")
   porosity.fill_normal(mean=0.24, std=0.03, zone="Base")

Or from an array restricted to a zone:

.. code-block:: python

   array = np.full(grid.shape, 0.24)
   porosity.from_array(array, zone="Base")

This allows each zone to be modeled independently while still storing the result
in a single grid property.

Interpolating Property Values from Wells
----------------------------------------

Properties can also be interpolated from well samples.

.. code-block:: python

   well1 = VerticalWell(name="Well 1", x=20, y=78)
   well3 = VerticalWell(name="Well 3", x=32, y=55)

   well1.add_sample(name="porosity", value=100, depth=10)
   well3.add_sample(name="porosity", value=50, depth=15)

   porosity.from_wells(
       wells=[well1, well3],
       interpolator=UKInterpolator(),
       mode="xyz",
   )

   porosity.show()

This workflow is useful when property measurements are available only at well
locations and must be distributed throughout the grid by interpolation.

The chosen interpolator controls how the well data are propagated spatially.
Depending on the problem, different interpolators may be more appropriate.

Filling Remaining Missing Values
--------------------------------

In some workflows, only part of a property is assigned initially. Any remaining
``NaN`` values can then be replaced using :meth:`fill_nan`.

.. code-block:: python

   porosity.fill_nan(0.0)

This is useful after partial assignment, zone-based modeling, or interpolation
when some cells remain undefined.

Complete Example
----------------

The following example combines several of the ideas introduced above.

.. code-block:: python

   from petres.grids import CornerPointGrid
   import numpy as np

   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )

   porosity = grid.properties.create(
       name="poro",
       eclipse_keyword="PORO",
       description="Porosity",
   )

   porosity.fill_normal(mean=0.24, std=0.03, min=0.20, max=0.30, seed=42)

   permeability = grid.properties.create(
       name="perm",
       eclipse_keyword="PERM",
       description="Permeability",
   )

   permeability.apply(
       lambda poro, z: 100 * poro**3 + z,
       source=(porosity, "z"),
   )

   print(porosity.summary())
   print(permeability.summary())

   porosity.show(cmap="viridis")
   permeability.show(cmap="plasma")

Where to Go Next
----------------

Now that you know how to define and populate cell properties, the next step is
usually to export the grid and its associated properties for simulation use.

Continue with:

- :doc:`grid-modeling-from-horizons-and-zones`
- :doc:`exporting-grid`

See Also
--------

- :doc:`pillar-gridding`
- :doc:`zone-modeling`
- :doc:`horizon-modeling`
- :class:`petres.grids.cornerpoint.CornerPointGrid`
- :class:`petres.properties.gridproperty.GridProperty`