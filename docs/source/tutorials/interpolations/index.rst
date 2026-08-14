Interpolations
==============

Interpolation in Petres converts sparse measurements, 
such as well tops and geological properties measured at wells (e.g., porosity and permeability), 
into spatial distributions for grid generation and static modeling.


Available Interpolators
-----------------------

Petres currently supports the following interpolators: 

.. toctree::
   :maxdepth: 1

   idw
   rbf
   kriging

Common Workflow
---------------

All Petres interpolators follow the same conceptual pipeline:

1. Create an interpolator instance with method-specific parameters.
2. Fit it on known coordinates and scalar values using the :meth:`fit` method.
3. Predict at given coordinates using the :meth:`predict` method.

.. code-block:: python

   import numpy as np
   from petres.interpolators import IDWInterpolator

   X = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0], [100.0, 100.0]])
   y = np.array([10.0, 12.0, 11.5, 13.0])

   interp = IDWInterpolator(power=2.0)
   interp.fit(X, y)

   Q = np.array([[50.0, 50.0], [25.0, 75.0]])
   pred = interp.predict(Q)

.. note::

   The same interpolator instances can be passed directly into Petres workflows,
   such as :class:`~petres.models.Horizon` construction.

You can import all interpolators from the :mod:`~petres.interpolators` namespace.


Using Interpolators in Petres Workflows
---------------------------------------

Petres interpolators can be used across different workflows, such as
horizon creation and property modeling. The following examples illustrate
typical usage patterns.

Creating a Horizon
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon

   horizon = Horizon(
      name="Top Reservoir",
      xy=[[0, 0], [100, 0], [0, 100], [100, 100]],
      depth=[1000, 1020, 1010, 1030],
      interpolator=IDWInterpolator(power=2.0, neighbors=8),
   )

Property Modeling from Well Samples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from petres.interpolators import UniversalKrigingInterpolator

   porosity.from_wells(
      wells=[well_1, well_2, well_3, well_4],
      interpolator=UniversalKrigingInterpolator(
         variogram_model="gaussian",
         drift_terms=["regional_linear"],
      ),
   )




