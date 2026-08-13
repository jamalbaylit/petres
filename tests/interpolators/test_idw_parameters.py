from __future__ import annotations

import numpy as np
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


def test_idw_rejects_non_positive_chunk_size():
    with pytest.raises(ValueError, match="chunk_size"):
        IDWInterpolator(chunk_size=0)


def test_idw_dtype_parameter():
    """Verify dtype parameter is properly set and used."""
    interp_f32 = IDWInterpolator(dtype=np.float32)
    interp_f64 = IDWInterpolator(dtype=np.float64)
    
    assert interp_f32.dtype == np.float32
    assert interp_f64.dtype == np.float64
    
    # Verify output dtype matches
    xy = np.array([[0.0, 0.0], [1.0, 1.0]])
    values = np.array([1.0, 2.0])
    
    interp_f32.fit(xy, values)
    pred_f32 = interp_f32.predict(np.array([[0.5, 0.5]]))
    assert pred_f32.dtype == np.float32
    
    interp_f64.fit(xy, values)
    pred_f64 = interp_f64.predict(np.array([[0.5, 0.5]]))
    assert pred_f64.dtype == np.float64


