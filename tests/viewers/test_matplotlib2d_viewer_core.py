from __future__ import annotations

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")

from petres.models import VerticalWell
from petres.viewers.viewer2d.matplotlib.theme import Matplotlib2DViewerTheme
from petres.viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer


def test_matplotlib2d_set_theme_requires_correct_type():
    viewer = Matplotlib2DViewer()
    obj = object()
    viewer.set_theme(obj)
    assert viewer.theme is obj


def test_matplotlib2d_show_sets_window_title(monkeypatch):
    viewer = Matplotlib2DViewer()

    calls = {"title": None}

    class DummyManager:
        def set_window_title(self, title):
            calls["title"] = title

    monkeypatch.setattr(viewer.fig.canvas, "manager", DummyManager(), raising=False)
    monkeypatch.setattr("petres.viewers.viewer2d.matplotlib.viewer.plt.show", lambda: None)

    viewer.show()

    assert calls["title"] == "Petres 2D Viewer"


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


def test_matplotlib2d_add_wells_single_and_sequence(monkeypatch):
    viewer = Matplotlib2DViewer(theme=Matplotlib2DViewerTheme())

    calls = []

    def _fake_add_well(ax, well_x, well_y, well_name, **kwargs):
        calls.append((ax, well_x, well_y, well_name, kwargs))

    monkeypatch.setattr("petres.viewers.viewer2d.matplotlib.viewer._add_well", _fake_add_well)

    w1 = VerticalWell(name="W1", x=10.0, y=20.0)
    w2 = VerticalWell(name="W2", x=30.0, y=40.0)

    out_single = viewer.add_wells(w1, marker_color="red")
    out_many = viewer.add_wells([w1, w2], marker="s")

    assert out_single is viewer
    assert out_many is viewer
    assert len(calls) == 3
    assert calls[0][1] == w1.x
    assert calls[0][2] == w1.y
    assert calls[0][3] == w1.name
    assert calls[0][4]["marker_color"] == "red"
    assert calls[2][1] == w2.x
    assert calls[2][2] == w2.y
    assert calls[2][3] == w2.name
    assert calls[2][4]["marker"] == "s"


def test_matplotlib2d_add_wells_rejects_invalid_input():
    viewer = Matplotlib2DViewer(theme=Matplotlib2DViewerTheme())

    with pytest.raises(TypeError):
        viewer.add_wells(123)
