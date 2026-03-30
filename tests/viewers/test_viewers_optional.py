from __future__ import annotations

import pytest

from petres.models import Horizon, Zone
from petres.viewers import Viewer2D, Viewer2DTheme


def test_viewer2d_public_aliases_exist():
    assert Viewer2D is not None
    assert Viewer2DTheme is not None


def test_viewer3d_alias_imports_when_pyvista_available():
    pytest.importorskip("pyvista")
    from petres.viewers import Viewer3D

    assert Viewer3D is not None


def test_horizon_show2d_delegates_to_matplotlib_viewer(monkeypatch, horizon_plane_top):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def add_horizon(self, *args, **kwargs):
            calls["added"] = True

        def show(self):
            calls["shown"] = True

    monkeypatch.setattr("petres.models.horizon.Matplotlib2DViewer", DummyViewer, raising=False)

    # patch import location used inside method
    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    horizon_plane_top.show2d(x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_zone_show2d_delegates_to_matplotlib_viewer(monkeypatch, horizon_plane_top, horizon_plane_base):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def add_zone(self, *args, **kwargs):
            calls["added"] = True

        def show(self):
            calls["shown"] = True

    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    zone.show2d(x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_boundary_show2d_delegates_to_matplotlib_viewer(monkeypatch, boundary_box):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def add_boundary_polygon(self, *args, **kwargs):
            calls["added"] = True

        def show(self):
            calls["shown"] = True

    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    boundary_box.show2d()

    assert calls["added"] and calls["shown"]
