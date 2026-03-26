from __future__ import annotations

import pytest

from petres.interpolators import IDWInterpolator


def test_idw_rejects_non_positive_power():
    with pytest.raises(ValueError, match="power"):
        IDWInterpolator(power=0.0)


def test_idw_rejects_non_positive_eps():
    with pytest.raises(ValueError, match="eps"):
        IDWInterpolator(eps=0.0)


def test_idw_rejects_non_positive_neighbors():
    with pytest.raises(ValueError, match="neighbors"):
        IDWInterpolator(neighbors=0)


def test_idw_rejects_unknown_mode():
    with pytest.raises(ValueError, match="mode"):
        IDWInterpolator(mode="invalid")
