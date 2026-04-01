"""Interpolation methods for petroleum and reservoir modeling.

Provides spatial interpolation techniques (IDW, RBF, kriging) for mapping sparse
data (e.g., wells, sample points) to grids and surfaces.

Examples
--------
>>> from petres.interpolators import IDWInterpolator
>>> idw = IDWInterpolator(power=2.0, neighbors=12)
>>> idw.fit(well_points, porosity_values)
>>> grid_porosity = idw.predict(grid_points)
"""

from .spatial.inverse_distance import InverseDistanceWeightingInterpolator
from .spatial.kriging import OrdinaryKrigingInterpolator, UniversalKrigingInterpolator
from .spatial.radial_basis import RadialBasisFunctionInterpolator

# Convenient aliases for public API
IDWInterpolator = InverseDistanceWeightingInterpolator
RBFInterpolator = RadialBasisFunctionInterpolator
OKInterpolator = OrdinaryKrigingInterpolator
UKInterpolator = UniversalKrigingInterpolator
__all__ = [
    'IDWInterpolator',
    'RBFInterpolator',
    'OKInterpolator',
    'UKInterpolator',

    'InverseDistanceWeightingInterpolator',
    'RadialBasisFunctionInterpolator',
    'OrdinaryKrigingInterpolator',
    'UniversalKrigingInterpolator',

]
