from __future__ import annotations


def test_horizon_show_calls_3d_viewer(monkeypatch, horizon_plane_top):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def add_horizon(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    monkeypatch.setattr("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer", DummyViewer)

    horizon_plane_top.show(x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_zone_show_calls_3d_viewer(monkeypatch, horizon_plane_top, horizon_plane_base):
    from petres.models import Zone

    calls = {"added": False, "shown": False}

    class DummyViewer:
        def add_zone(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    monkeypatch.setattr("petres.viewers.viewer3d.pyvista.viewer.PyVista3DViewer", DummyViewer)

    zone = Zone("Z", top=horizon_plane_top, base=horizon_plane_base)
    zone.show(x=[0, 10], y=[0, 10])

    assert calls["added"] and calls["shown"]


def test_boundary_show_calls_2d_viewer(monkeypatch, boundary_box):
    calls = {"added": False, "shown": False}

    class DummyViewer:
        def __init__(self, *args, **kwargs):
            pass

        def add_boundary_polygon(self, *args, **kwargs):
            calls["added"] = True

        def show(self, *args, **kwargs):
            calls["shown"] = True

    monkeypatch.setattr("petres.viewers.viewer2d.matplotlib.viewer.Matplotlib2DViewer", DummyViewer)

    boundary_box.show()

    assert calls["added"] and calls["shown"]
