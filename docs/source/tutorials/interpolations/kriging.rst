.. _kriging-tutorials:

Kriging Interpolators
=====================

.. _ok-tutorials:

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

.. _uk-tutorials:

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

