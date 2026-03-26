from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import IDWInterpolator


def test_fit_predict_exact_sample_returns_exact_value():
    xy = np.array([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    values = np.array([10.0, 20.0, 30.0])

    interp = IDWInterpolator(power=2.0)
    interp.fit(xy, values)

    pred = interp.predict(np.array([[1.0, 0.0]]))
    np.testing.assert_allclose(pred, [20.0], atol=1e-12)


def test_predict_before_fit_raises_runtime_error():
    interp = IDWInterpolator()
    with pytest.raises(RuntimeError, match="must be fitted"):
        interp.predict(np.array([[0.0, 0.0]]))


def test_fit_rejects_mismatched_sample_count():
    interp = IDWInterpolator()
    xy = np.array([[0.0, 0.0], [1.0, 1.0]])
    values = np.array([1.0])
    with pytest.raises(ValueError, match="same n_samples"):
        interp.fit(xy, values)


def test_fit_rejects_nan_coordinates():
    interp = IDWInterpolator()
    xy = np.array([[0.0, np.nan], [1.0, 1.0]])
    values = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="NaN"):
        interp.fit(xy, values)


def test_predict_rejects_dim_mismatch_after_fit():
    interp = IDWInterpolator()
    interp.fit(np.array([[0.0, 0.0], [1.0, 0.0]]), np.array([1.0, 2.0]))
    with pytest.raises(ValueError, match="dim mismatch"):
        interp.predict(np.array([[0.0, 0.0, 0.0]]))


def test_neighbors_greater_than_samples_raises():
    interp = IDWInterpolator(neighbors=5)
    with pytest.raises(ValueError, match="cannot be greater than"):
        interp.fit(np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([1.0, 2.0]))


def test_knn_and_full_idw_match_for_neighbors_equal_n():
    xy = np.array([[0.0, 0.0], [100.0, 0.0], [0.0, 100.0]])
    values = np.array([1.0, 2.0, 3.0])
    q = np.array([[25.0, 25.0], [60.0, 30.0]])

    full = IDWInterpolator(power=2.0)
    full.fit(xy, values)

    knn = IDWInterpolator(power=2.0, neighbors=3)
    knn.fit(xy, values)

    np.testing.assert_allclose(full.predict(q), knn.predict(q), rtol=1e-12, atol=1e-12)


def test_predict_empty_query_returns_empty_array():
    interp = IDWInterpolator()
    interp.fit(np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([1.0, 2.0]))
    pred = interp.predict(np.empty((0, 2)))
    assert pred.shape == (0,)
