"""Interpolation methods for petroleum and reservoir modeling.

Provides various interpolation techniques for mapping sparse domain data
(e.g., well logs, sample points) to grids and surfaces.

Interpolators:
    InverseDistanceWeightingInterpolator (alias: IDWInterpolator)
        Shepard's IDW method for local weighted averaging
    
    LinearInterpolator
        Triangulation-based and regular grid linear interpolation
    
    RadialBasisFunctionInterpolator (alias: RBFInterpolator)
        Smooth RBF interpolation with various kernel functions
    
    NearestNeighborInterpolator (alias: NNInterpolator)
        Simple nearest neighbor interpolation

Example:
    >>> from petromod.interpolators import IDWInterpolator
    >>> idw = IDWInterpolator(power=2.0, max_neighbors=12)
    >>> idw.fit(well_points, porosity_values)
    >>> grid_porosity = idw.interpolate(grid_points)
"""

from .base import InterpolatorBase
from .spatial.inverse_distance import InverseDistanceWeightingInterpolator
from .spatial.linear import LinearInterpolator
from .spatial.radial_basis import RadialBasisFunctionInterpolator, RBF_KERNELS
from .spatial.nearest_neighbor import NearestNeighborInterpolator


# Convenient aliases for public API
IDWInterpolator = InverseDistanceWeightingInterpolator
RBFInterpolator = RadialBasisFunctionInterpolator
NNInterpolator = NearestNeighborInterpolator

__all__ = [
    # Base class
    # 'InterpolatorBase',
    # Full names
    'InverseDistanceWeightingInterpolator',
    'LinearInterpolator',
    'RadialBasisFunctionInterpolator',
    # 'NearestNeighborInterpolator',
    # Convenient aliases
    'IDWInterpolator',
    'RBFInterpolator',
    'NNInterpolator',
    # Constants
    'RBF_KERNELS',
]
