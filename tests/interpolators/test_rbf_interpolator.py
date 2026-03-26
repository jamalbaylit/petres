from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import RBFInterpolator


def _xy_plane_samples() -> tuple[np.ndarray, np.ndarray]:
    x = np.array([0.0, 1.0, 0.0, 1.0, 0.5])
    y = np.array([0.0, 0.0, 1.0, 1.0, 0.25])
    xy = np.column_stack([x, y])
    values = 10.0 + 2.0 * x + 3.0 * y
    return xy, values


def test_rbf_fit_predict_returns_finite_values():
    xy, values = _xy_plane_samples()
    q = np.array([[0.25, 0.25], [0.75, 0.75], [0.4, 0.2]])

    interp = RBFInterpolator(kernel="linear", smoothing=0.0)
    interp.fit(xy, values)
    pred = interp.predict(q)

    assert pred.shape == (3,)
    assert np.all(np.isfinite(pred))


def test_rbf_interpolates_training_points_when_smoothing_zero():
    xy, values = _xy_plane_samples()
    interp = RBFInterpolator(kernel="linear", smoothing=0.0)
    interp.fit(xy, values)

    pred = interp.predict(xy)
    np.testing.assert_allclose(pred, values, atol=1e-8)


def test_rbf_predict_empty_query_returns_empty():
    xy, values = _xy_plane_samples()
    interp = RBFInterpolator()
    interp.fit(xy, values)

    pred = interp.predict(np.empty((0, 2)))
    assert pred.shape == (0,)


def test_rbf_rejects_invalid_constructor_params():
    with pytest.raises(ValueError, match="epsilon"):
        RBFInterpolator(epsilon=0.0)
    with pytest.raises(ValueError, match="smoothing"):
        RBFInterpolator(smoothing=-1.0)
    with pytest.raises(ValueError, match="neighbors"):
        RBFInterpolator(neighbors=0)
    with pytest.raises(ValueError, match="degree"):
        RBFInterpolator(degree=-1)


def test_rbf_rejects_neighbors_greater_than_n_samples():
    xy, values = _xy_plane_samples()
    interp = RBFInterpolator(neighbors=20)

    with pytest.raises(ValueError, match="cannot be greater than"):
        interp.fit(xy, values)


def test_rbf_rejects_dim_mismatch_at_predict():
    xy, values = _xy_plane_samples()
    interp = RBFInterpolator()
    interp.fit(xy, values)

    with pytest.raises(ValueError, match="predict dim mismatch"):
        interp.predict(np.array([[0.1, 0.2, 0.3]]))


def test_rbf_rejects_invalid_fit_shapes():
    interp = RBFInterpolator()
    with pytest.raises(ValueError, match="coordinates must be 2D"):
        interp.fit(np.array([0.0, 1.0]), np.array([1.0, 2.0]))

    with pytest.raises(ValueError, match="same n_samples"):
        interp.fit(np.array([[0.0, 0.0], [1.0, 1.0]]), np.array([1.0]))
