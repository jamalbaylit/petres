.. _idw-fundamentals:

Inverse Distance Weighting
==========================

Inverse Distance Weighting (IDW) is a simple and widely used interpolation
method for estimating values at locations where no measurements are
available.

The main idea is intuitive: nearby samples should have more influence than
far-away samples. For example, if you have measured reservoir properties at
a set of spatial locations, IDW can estimate the property at an arbitrary
location by taking a distance-weighted average of the known samples.

For a target location :math:`\mathbf{x}`, the estimated value is given by:

.. math::

   \hat{z}(\mathbf{x})
   =
   \frac{
       \displaystyle\sum_{i=1}^{n} w_i(\mathbf{x}) z_i
   }{
       \displaystyle\sum_{i=1}^{n} w_i(\mathbf{x})
   }

where:

* :math:`\hat{z}(\mathbf{x})` is the estimated value at the target location.
* :math:`z_i` is the known value of sample :math:`i`.
* :math:`w_i(\mathbf{x})` is the weight assigned to sample :math:`i`.
* :math:`n` is the number of known samples.

The weight assigned to each sample depends on its distance from the target
location. In IDW, the weight is inversely proportional to the distance
raised to a power:

.. math::

   w_i(\mathbf{x})
   =
   \frac{1}
   {\left(d_i(\mathbf{x}) + \varepsilon\right)^p}

where:

* :math:`d_i(\mathbf{x})` is the distance between the target location and
  sample :math:`i`.
* :math:`p` is the power parameter, which controls how strongly the
  influence of distance decays.
* :math:`\varepsilon` is a small positive value introduced to avoid division
  by zero when the target location coincides with a known sample location.

The distance determines how strongly each known sample influences the
estimated value. Closer samples receive larger weights, while farther
samples receive smaller weights.

The power parameter controls the rate at which this influence decreases
with distance:

* Smaller :math:`p` values produce a more gradual decrease in influence,
  allowing distant samples to retain more weight.
* Larger :math:`p` values produce a faster decrease in influence, causing
  nearby samples to dominate more strongly.

A commonly used value is :math:`p=2`, although the appropriate value depends
on the spatial characteristics of the data and the application.

The :math:`\varepsilon` term is used to make the distance-based weighting
numerically well-defined when :math:`d_i(\mathbf{x}) = 0`. Without this
term, the corresponding weight would involve division by zero. The value of
:math:`\varepsilon` is typically chosen to be very small so that it has
negligible influence on the weights when the distance is nonzero.

An alternative approach is to handle coincident locations explicitly. If a
target location exactly coincides with a known sample location, the
interpolation can simply return the value of that sample rather than
evaluating the inverse-distance weights. Using a small :math:`\varepsilon`
provides a convenient numerical alternative to this special-case treatment.

Combining the weighted-average equation with the IDW weight definition gives
the complete formulation:

.. math::

   \hat{z}(\mathbf{x})
   =
   \frac{
       \displaystyle\sum_{i=1}^{n}
       \frac{z_i}
       {\left(d_i(\mathbf{x})+\varepsilon\right)^p}
   }{
       \displaystyle\sum_{i=1}^{n}
       \frac{1}
       {\left(d_i(\mathbf{x})+\varepsilon\right)^p}
   }
