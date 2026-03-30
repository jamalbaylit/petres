from __future__ import annotations

from petres.interpolators import (
    IDWInterpolator,
    InverseDistanceWeightingInterpolator,
    OKInterpolator,
    OrdinaryKrigingInterpolator,
    RBFInterpolator,
    RadialBasisFunctionInterpolator,
    UKInterpolator,
    UniversalKrigingInterpolator,
)


def test_public_aliases_map_to_expected_classes():
    assert IDWInterpolator is InverseDistanceWeightingInterpolator
    assert RBFInterpolator is RadialBasisFunctionInterpolator
    assert OKInterpolator is OrdinaryKrigingInterpolator
    assert UKInterpolator is UniversalKrigingInterpolator
