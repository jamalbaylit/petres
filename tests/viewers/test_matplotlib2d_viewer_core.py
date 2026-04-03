from __future__ import annotations

import numpy as np
import pytest

from petres.viewers.viewer2d.matplotlib.theme import Matplotlib2DViewerTheme
from petres.viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer


def test_matplotlib2d_set_theme_requires_correct_type():
    viewer = Matplotlib2DViewer()
    obj = object()
    viewer.set_theme(obj)
    assert viewer.theme is obj


def test_matplotlib2d_add_horizon_returns_self(monkeypatch, horizon_plane_top):
    viewer = Matplotlib2DViewer(theme=Matplotlib2DViewerTheme())

    monkeypatch.setattr(
        "petres.viewers.viewer2d.matplotlib.viewer._resolve_xy_vertices",
        lambda **kwargs: (np.array([0.0, 1.0]), np.array([0.0, 1.0])),
    )

    called = {"ok": False}

    def _fake_add_surface(*args, **kwargs):
        called["ok"] = True

    monkeypatch.setattr("petres.viewers.viewer2d.matplotlib.viewer._add_surface", _fake_add_surface)

    out = viewer.add_horizon(horizon_plane_top, x=np.array([0.0, 1.0]), y=np.array([0.0, 1.0]))

    assert out is viewer
    assert called["ok"]


def test_matplotlib2d_add_zone_returns_self(monkeypatch, horizon_plane_top, horizon_plane_base):
    from petres.models import Zone

    viewer = Matplotlib2DViewer(theme=Matplotlib2DViewerTheme())
    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)

    monkeypatch.setattr(
        "petres.viewers.viewer2d.matplotlib.viewer._resolve_xy_vertices",
        lambda **kwargs: (np.array([0.0, 1.0]), np.array([0.0, 1.0])),
    )

    called = {"ok": False}

    def _fake_add_surface(*args, **kwargs):
        called["ok"] = True

    monkeypatch.setattr("petres.viewers.viewer2d.matplotlib.viewer._add_surface", _fake_add_surface)

    out = viewer.add_zone(zone, x=np.array([0.0, 1.0]), y=np.array([0.0, 1.0]))

    assert out is viewer
    assert called["ok"]
