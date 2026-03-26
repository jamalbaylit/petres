from __future__ import annotations

import numpy as np
import pytest

from petres.interpolators import OKInterpolator, UKInterpolator


pytest.importorskip("pykrige")


def _xy_samples() -> tuple[np.ndarray, np.ndarray]:
    xy = np.array(
        [
            [0.0, 0.0],
            [1.0, 0.0],
            [0.0, 1.0],
            [1.0, 1.0],
            [0.5, 0.3],
        ],
        dtype=float,
    )
    values = 100.0 + 5.0 * xy[:, 0] + 2.0 * xy[:, 1]
    return xy, values


def _xyz_samples() -> tuple[np.ndarray, np.ndarray]:
    xyz = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.2],
            [0.0, 1.0, 0.5],
            [1.0, 1.0, 0.8],
            [0.5, 0.4, 0.6],
            [0.2, 0.8, 0.3],
        ],
        dtype=float,
    )
    values = 10.0 + 3.0 * xyz[:, 0] + 2.0 * xyz[:, 1] + 1.5 * xyz[:, 2]
    return xyz, values


def test_ok_interpolator_predicts_and_returns_variance_2d():
    xy, values = _xy_samples()
    q = np.array([[0.25, 0.25], [0.75, 0.75]])

    interp = OKInterpolator(variogram_model="linear", nlags=4)
    interp.fit(xy, values)

    pred = interp.predict(q)
    var = interp.predict_variance(q)

    assert pred.shape == (2,)
    assert var.shape == (2,)
    assert np.all(np.isfinite(pred))
    assert np.all(np.isfinite(var))
    assert np.all(var >= 0.0)


def test_ok_interpolator_supports_3d_inputs():
    xyz, values = _xyz_samples()
    q = np.array([[0.3, 0.2, 0.4], [0.9, 0.7, 0.6]])

    interp = OKInterpolator(variogram_model="linear", nlags=4)
    interp.fit(xyz, values)

    pred, var = interp.predict_with_variance(q)

    assert pred.shape == (2,)
    assert var.shape == (2,)
    assert np.all(np.isfinite(pred))


def test_ok_constructor_rejects_invalid_configuration():
    with pytest.raises(ValueError, match="nlags"):
        OKInterpolator(nlags=0)
    with pytest.raises(ValueError, match="pseudo_inv_type"):
        OKInterpolator(pseudo_inv_type="bad")
    with pytest.raises(ValueError, match="backend"):
        OKInterpolator(backend="bad")
    with pytest.raises(ValueError, match="coordinates_type"):
        OKInterpolator(coordinates_type="bad")


def test_ok_fit_rejects_unsupported_dimension():
    x1d = np.array([[0.0], [1.0], [2.0]])
    y = np.array([1.0, 2.0, 3.0])
    interp = OKInterpolator()

    with pytest.raises(ValueError, match="supports dims"):
        interp.fit(x1d, y)


def test_uk_interpolator_predicts_with_functional_drift_2d():
    xy, values = _xy_samples()
    q = np.array([[0.2, 0.3], [0.8, 0.9]])

    interp = UKInterpolator(
        variogram_model="linear",
        drift_terms=["functional"],
        functional_drift=[lambda x, y: x + y],
        nlags=4,
        backend="loop",
    )
    interp.fit(xy, values)

    pred = interp.predict(q)
    var = interp.predict_variance(q)

    assert pred.shape == (2,)
    assert var.shape == (2,)
    assert np.all(np.isfinite(pred))


def test_uk_rejects_backend_c():
    with pytest.raises(ValueError, match="not supported"):
        UKInterpolator(backend="C")


def test_uk_rejects_invalid_drift_term_for_dimension():
    xyz, values = _xyz_samples()
    interp = UKInterpolator(drift_terms=["point_log"])

    with pytest.raises(ValueError, match="Unsupported drift term"):
        interp.fit(xyz, values)


def test_uk_rejects_non_callable_functional_drift():
    xy, values = _xy_samples()
    interp = UKInterpolator(drift_terms=["functional"], functional_drift=[123])

    with pytest.raises(TypeError, match="callable"):
        interp.fit(xy, values)


def test_uk_rejects_mismatched_specified_drift_length():
    xy, values = _xy_samples()
    interp = UKInterpolator(drift_terms=["specified"], specified_drift=[np.array([1.0, 2.0])])

    with pytest.raises(ValueError, match="length must match"):
        interp.fit(xy, values)
