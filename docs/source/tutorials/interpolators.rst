Interpolators
=============

Interpolation in Petres converts sparse measurements—such as 
sample points, well tops, or well property samples—into a spatial 
distribution that can be evaluated at any location. 
Petres currently supports the following interpolators: 
**Inverse Distance Weighting (IDW)**, **Radial Basis Function (RBF)**,
**Ordinary Kriging**, and **Universal Kriging**.

Common workflow
---------------

All Petres interpolators follow the same conceptual pipeline:

1. Create an interpolator instance with method-specific parameters.
2. Fit it on known coordinates and scalar values using the :meth:`fit` method.
3. Predict at query coordinates using the :meth:`predict` method.

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
   such as :class:`~petres.models.Horizon` construction and
   :meth:`~petres.grids.properties.GridProperty.from_wells`.

You can import all interpolators from the :mod:`~petres.interpolators` namespace.

.. _idw-interpolation:

Inverse Distance Weighting (IDW)
--------------------------------

The :class:`~petres.interpolators.InverseDistanceWeightingInterpolator`
(available as :class:`~petres.interpolators.IDWInterpolator` for convenience) estimates values at unknown
locations by assigning larger weights to nearby samples and smaller weights
to distant ones. proportional to the inverse of their distance raised to a power:


.. math::

   w_i = \frac{1}{(d_i + \varepsilon)^p}, \quad
   \hat{v}(q) = \frac{\sum_i w_i v_i}{\sum_i w_i}

where :math:`d_i` is the distance to sample :math:`i`, :math:`p` controls how
quickly influence decreases with distance, :math:`\varepsilon` is a small
stabilization term, and :math:`q` is the query point. If a query point exactly
matches a sample location, the known value is returned directly.

In practice, these quantities are controlled through the interpolator parameters:

- ``power``: Controls how strongly nearby points dominate the interpolation. A higher value makes the interpolated values more sensitive to nearby samples, while distant samples contribute very little. Lower values allow distant points to have more influence. Default: ``2.0``.

- ``eps``: A small positive number added to the distance to prevent division by zero. This stabilizes the computation when query points coincide or are very close to sample points. Default: ``1e-8``.

- ``neighbors``: Sets the maximum number of nearest samples considered when predicting a value at a query point. Limiting the number of neighbors can improve computation speed and reduce the influence of distant points. If ``None``, all samples are used. Default: ``None``.

- ``mode``: Determines how the weighted values are aggregated. The ``"average"`` mode normalizes the weights to produce an average value, while ``"sum"`` returns the unnormalized weighted sum. Default: ``"average"``.


By default, all fitted sample points contribute to each prediction, although
distant samples receive very small (often negligible) weights. To restrict
the interpolation to nearby samples, use the ``neighbors`` parameter.

.. code-block:: python

   from petres.interpolators import IDWInterpolator

   interp = IDWInterpolator(power=2.0, neighbors=12, mode="average")
   interp.fit(X, y)
   pred = interp.predict(Q)

.. important::

   Ensure that the dimensions of the prediction coordinates match those used during fitting.


.. _rbf-interpolation:

Radial Basis Function (RBF)
---------------------------

:class:`~petres.interpolators.RadialBasisFunctionInterpolator` 
(aliased as ``RBFInterpolator``) wraps 
:class:`scipy.interpolate.RBFInterpolator` for use in Petres workflows. 
It can be configured using the following parameters: 

- ``kernel``: Specifies the type of radial basis function used to calculate the influence of each sample point. Common options include ``"linear"`` (linearly decreasing influence), ``"cubic"`` (cubic decrease), ``"thin_plate_spline"`` (smooth spline minimizing bending energy), and ``"gaussian"`` (bell-shaped influence controlled by epsilon). The choice of kernel determines the overall smoothness of the interpolated surface. Default: ``"linear"``.

- ``epsilon``: A shape parameter for kernels such as ``"gaussian"``. It controls the width of each point’s influence. Larger values produce smoother, more global effects, while smaller values create sharper, more localized peaks. Default: ``1.0``.

- ``neighbors``: Limits the number of nearest samples considered for each query point. Using fewer neighbors can reduce computation and limit the effect of distant points. If ``None``, all samples are considered. Default: ``None``.

- ``smoothing``: Controls how closely the interpolator fits the input data. A value of ``0`` gives exact interpolation, reproducing all sample points. Positive values introduce smoothing, which is helpful for noisy datasets. Default: ``0.0``.

A typical usage looks like this:

.. code-block:: python

   from petres.interpolators import RBFInterpolator

   interp = RBFInterpolator(kernel="gaussian", epsilon=2.0, smoothing=0.1)
   interp.fit(X, y)
   predictions = interp.predict(Q)


.. _ok-interpolation:

Ordinary Kriging Interpolator
-----------------------------

The :class:`~petres.interpolators.OrdinaryKrigingInterpolator` (aliased as ``OKInterpolator``) 
performs ordinary kriging in 2D or 3D, 
automatically selecting the appropriate PyKrige backend 
(:class:`pykrige.ok.OrdinaryKriging` or :class:`pykrige.ok3d.OrdinaryKriging3D`)
based on input dimensions. 



- ``variogram_model``: Defines the mathematical model for spatial correlation. Available options are ``"linear"``, ``"power"``, ``"gaussian"``, ``"spherical"``, ``"exponential"``, ``"hole-effect"``, and ``"custom"``. Each model describes how semivariance increases with distance. Default: ``"linear"``.

- ``variogram_parameters``: Explicit parameters for the chosen variogram model. Can be a dictionary, a sequence of floats, or ``None``. If ``None``, PyKrige estimates parameters automatically. Default: ``None``.

- ``variogram_function``: A custom callable function used when ``variogram_model="custom"``. Must accept distances and return semivariance values. Default: ``None``.

- ``nlags``: The number of lag bins used to compute the experimental variogram. Must be an integer ≥1. Default: ``6``.

- ``weight``: Determines whether semivariance values are weighted by the number of point pairs in each bin. Default: ``False``.

- ``verbose``: If ``True``, prints log messages during variogram fitting and execution. Default: ``False``.

- ``enable_plotting``: Displays plots of the variogram fit when ``True``. Default: ``False``.

- ``exact_values``: If ``True``, ensures that interpolated values exactly reproduce training values at sampled points. Default: ``True``.

- ``pseudo_inv``: Use a pseudo-inverse to solve the kriging system, useful for ill-conditioned matrices. Default: ``False``.

- ``pseudo_inv_type``: Specifies which pseudo-inverse algorithm to use. Options are ``"pinv"`` (default) and ``"pinvh"``. Default: ``"pinv"``.

- ``backend``: Execution backend for PyKrige; options are ``"vectorized"`` (fast, default), ``"loop"`` (slower Python loops), or ``"C"`` (C-accelerated). Default: ``"vectorized"``.

- ``anisotropy_scaling``: Controls anisotropy in the spatial correlation. Scalar for 2D, or tuple ``(scaling_y, scaling_z)`` for 3D, specifying scaling along each axis. Default: ``1.0``.

- ``anisotropy_angle``: Rotation angles to apply for anisotropy. Scalar in 2D or tuple ``(angle_x, angle_y, angle_z)`` in 3D. Default: ``0.0``.

- ``coordinates_type``: Specifies interpretation of 2D coordinates; ``"euclidean"`` for Cartesian, ``"geographic"`` for latitude/longitude. Default: ``"euclidean"``.

Usage Example:

.. code-block:: python

   from petres.interpolators import OrdinaryKrigingInterpolator

   interp = OrdinaryKrigingInterpolator(
      variogram_model="spherical",
      nlags=8,
      enable_plotting=True,
   )
   interp.fit(X, y)
   predictions = interp.predict(Q)

.. _uk-interpolation:

Universal Kriging Interpolator
------------------------------

The :class:`~petres.interpolators.UniversalKrigingInterpolator` extends ordinary kriging by 
supporting drift terms, including regional, specified, or functional drifts. 
It implements PyKrige's :class:`pykrige.uk.UniversalKriging` and :class:`pykrige.uk3d.UniversalKriging3D` classes, 
automatically selecting the appropriate backend based on input dimensions. 
You can also use :class:`~petres.interpolators.UKInterpolator` as a convenient alias.

All parameters from :class:`~petres.interpolators.OrdinaryKrigingInterpolator` are supported. Additional parameters:

- ``drift_terms``: List of drift types to include. Options include ``"regional_linear"`` (linear trend across the domain), ``"specified"`` (user-provided drift), and ``"functional"`` (callable functions). Default: ``None``.

- ``point_drift``: Drift values at sample points, used in 2D universal kriging. Default: ``None``.

- ``external_drift``: External raster array for 2D universal kriging. Default: ``None``.

- ``external_drift_x``: X-coordinates corresponding to ``external_drift``. Default: ``None``.

- ``external_drift_y``: Y-coordinates corresponding to ``external_drift``. Default: ``None``.

- ``specified_drift``: List of arrays specifying per-sample drift for ``"specified"`` drift terms. Default: ``None``.

- ``functional_drift``: List of callables for ``"functional"`` drift. Each function should accept coordinates and return drift values. Default: ``None``.

Examples for drift terms can be arrays or functions depending on the chosen drift type. Typical usage:

.. code-block:: python

   from petres.interpolators import UniversalKrigingInterpolator

   interp = UniversalKrigingInterpolator(
      variogram_model="exponential",
      drift_terms=["regional_linear", "specified"],
      specified_drift=[drift_array],
      enable_plotting=True,
   )
   interp.fit(X, y)
   predictions = interp.predict(Q)

.. note::
   You can use ``enable_plotting=True`` to visually assess variogram fits and drift effects.  


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

