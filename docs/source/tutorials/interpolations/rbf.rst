.. _rbf-tutorials:

Radial Basis Function (RBF)
===========================

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
