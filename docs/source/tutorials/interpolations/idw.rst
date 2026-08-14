.. _idw-tutorials:

Inverse Distance Weighting (IDW)
================================

Inverse Distance Weighting (IDW) is available in Petres through
:class:`~petres.interpolators.InverseDistanceWeightingInterpolator`
or its shorter alias
:class:`~petres.interpolators.IDWInterpolator`.

For the mathematical formulation and a detailed explanation of how IDW works,
see :ref:`Inverse Distance Weighting Fundamentals <idw-fundamentals>`.

Basic Example
-------------

The following example interpolates values at two target locations from four
known samples in a 2D domain:

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   import numpy as np

   # Coordinates of the known samples
   X = np.array([
      [0.0, 0.0],
      [100.0, 0.0],
      [0.0, 100.0],
      [100.0, 100.0],
   ])

   # Known values at the sample locations
   y = np.array([10.0, 12.0, 11.5, 13.0])

   # Create and fit the interpolator
   interp = IDWInterpolator(power=2.0)
   interp.fit(X, y)

   # Target locations where values are to be estimated
   Q = np.array([
      [50.0, 50.0],
      [25.0, 75.0],
   ])

   # Estimate values at the target locations
   pred = interp.predict(Q)

Here:

* ``X`` contains the coordinates of the known samples.
* ``y`` contains the known values associated with those samples.
* ``Q`` contains the target locations where values are to be estimated.
* ``pred`` contains the estimated values at the target locations.

Configuring the Interpolator
----------------------------

The most important parameters are ``power``, ``eps``, and ``neighbors``:

.. code-block:: python

   interp = IDWInterpolator(
      power=2.0,
      eps=1e-12,
      neighbors=8,
   )

``power`` controls how strongly distance affects the interpolation. Larger
values give nearby samples more influence and produce more local interpolation.

``eps`` is a small value used to avoid division by zero when a target location
coincides with a known sample. The default value is normally appropriate and
does not need to be changed unless you have a specific numerical reason to do
so.

``neighbors`` limits the calculation to the ``k`` nearest samples for each
target location. This can substantially reduce computation for large datasets
and makes the interpolation more local.

For small datasets, or when using all available samples is appropriate,
``neighbors`` can be left as ``None``:


Memory and Precision
~~~~~~~~~~~~~~~~~~~~

For large datasets, IDW can require a significant amount of memory because
distances and weights must be calculated for many sample and target points.
Petres provides ``chunk_size`` to control how many target points are processed at once.

For example:

.. code-block:: python

   interp = IDWInterpolator(
      chunk_size=20000,
   )

A smaller ``chunk_size`` reduces peak memory usage at the cost of additional
processing batches. A larger value can improve performance when sufficient
memory is available.

If ``chunk_size`` is not specified, Petres processes all target points at once.
For small datasets where memory usage is not a concern, this is usually
sufficient.

The ``dtype`` parameter controls the numerical precision used for the cached
arrays and outputs. Lower-precision types can reduce memory usage for large
datasets:

.. code-block:: python

   interp = InverseDistanceWeightingInterpolator(
      power=2.0,
      dtype=np.float32,
   )

The default is ``np.float64``, which provides higher numerical precision.
Using ``np.float32`` can be useful when memory usage is important and the
reduced precision is acceptable for the application.

For most small or moderate-sized interpolation problems, the default settings
are sufficient. The ``neighbors``, ``chunk_size``, and ``dtype`` parameters
become particularly useful when working with large datasets.