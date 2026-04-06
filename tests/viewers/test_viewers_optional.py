from __future__ import annotations

import pytest

from petres.grids import PillarGrid
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
        def __init__(self, *args, **kwargs):
            pass

        def add_horizon(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    monkeypatch.setattr("petres.models.horizon.Matplotlib2DViewer", DummyViewer, raising=False)

    # patch import location used inside method
    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    horizon_plane_top.show(view="2d", x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_zone_show2d_delegates_to_matplotlib_viewer(monkeypatch, horizon_plane_top, horizon_plane_base):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def __init__(self, *args, **kwargs):
            pass

        def add_zone(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    zone.show2d(x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_boundary_show2d_delegates_to_matplotlib_viewer(monkeypatch, boundary_box):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def __init__(self, *args, **kwargs):
            pass

        def add_boundary_polygon(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    import petres.viewers.viewer2d.matplotlib.viewer as viewer_mod
    monkeypatch.setattr(viewer_mod, "Matplotlib2DViewer", DummyViewer)

    boundary_box.show()

    assert calls["added"] and calls["shown"]


def test_pillar_grid_show_delegates_to_pyvista_viewer(monkeypatch, simple_pillar_grid):
    calls = {"added": False, "shown": False, "pillars": None}

    class DummyViewer:
        def __init__(self, *args, **kwargs):
            pass

        def add_pillars(self, pillars, *args, **kwargs):
            calls["added"] = True
            calls["pillars"] = pillars

        def show(self, *args, **kwargs):
            calls["shown"] = True

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    monkeypatch.setattr(viewer_mod, "PyVista3DViewer", DummyViewer)

    simple_pillar_grid.show(title="Pillars")

    assert calls["added"] and calls["shown"]
    assert calls["pillars"] is simple_pillar_grid


def test_add_pillars_forwards_raw_arrays(monkeypatch, simple_pillar_grid):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    calls = {}

    def fake_add_pillars(backend, pillar_top, pillar_bottom, **kwargs):
        calls["backend"] = backend
        calls["pillar_top"] = pillar_top
        calls["pillar_bottom"] = pillar_bottom
        calls["kwargs"] = kwargs

    monkeypatch.setattr(viewer_mod, "_add_pillars", fake_add_pillars)

    viewer = object.__new__(viewer_mod.PyVista3DViewer)
    viewer.add_pillars(simple_pillar_grid, color="red", line_width=4.0)

    assert calls["backend"] is viewer
    assert calls["pillar_top"] is simple_pillar_grid.pillar_top
    assert calls["pillar_bottom"] is simple_pillar_grid.pillar_bottom
    assert calls["kwargs"]["color"] == "red"
    assert calls["kwargs"]["line_width"] == 4.0
