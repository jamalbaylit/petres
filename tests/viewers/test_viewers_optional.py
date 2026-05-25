from __future__ import annotations

import pytest

from petres.grids import PillarGrid
from petres.models import Horizon, VerticalWell, Zone
from petres.viewers import Viewer2D, Viewer2DTheme


class _DummyActor:
    def SetScale(self, *args):
        return None


class _DummyCamera:
    def __init__(self):
        self.zoom_calls = []

    def zoom(self, factor):
        self.zoom_calls.append(factor)

    def copy(self):
        return "cached-camera"


class _DummyRenderWindow:
    def __init__(self, size=(800, 600)):
        self._size = size

    def GetSize(self):
        return self._size


class _DummyInteractor:
    def __init__(self):
        self.observers = {}

    def AddObserver(self, event, callback):
        self.observers[event] = callback


class _DummyIren:
    def __init__(self):
        self.interactor = _DummyInteractor()


class _DummyPlotter:
    def __init__(self, off_screen=False):
        self.off_screen = off_screen
        self.theme = type("Theme", (), {"allow_empty_mesh": True})()
        self.camera = _DummyCamera()
        self.render_window = _DummyRenderWindow()
        self.iren = _DummyIren()
        self.bounds = (0.0, 100.0, 0.0, 200.0, 0.0, 300.0)
        self.background_color = None
        self.screenshot_calls = []
        self.camera_position = None
        self.show_calls = []
        self.close_calls = []

    def add_mesh(self, *args, **kwargs):
        return _DummyActor()

    def add_point_labels(self, *args, **kwargs):
        return None

    def add_lines(self, *args, **kwargs):
        return None

    def show_bounds(self, *args, **kwargs):
        return None

    def show_axes(self):
        return None

    def hide_axes(self):
        return None

    def set_background(self, *args, **kwargs):
        return None

    def add_text(self, *args, **kwargs):
        return None

    def reset_camera(self):
        return None

    def reset_camera_clipping_range(self):
        return None

    def screenshot(self, path, window_size=None):
        self.screenshot_calls.append((path, window_size))

    def show(self, *args, **kwargs):
        self.show_calls.append((args, kwargs))

    def close(self):
        self.close_calls.append(True)
        callback = self.iren.interactor.observers.get("ExitEvent")
        if callback is not None:
            callback(None, None)


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
    viewer.plotter = _DummyPlotter()
    viewer.add_pillars(simple_pillar_grid, color="red", line_width=4.0)

    assert calls["backend"] is viewer.plotter
    assert calls["pillar_top"] is simple_pillar_grid.pillar_top
    assert calls["pillar_bottom"] is simple_pillar_grid.pillar_bottom
    assert calls["kwargs"]["color"] == "red"
    assert calls["kwargs"]["line_width"] == 4.0


def test_add_wells_forwards_raw_wells_and_customization(monkeypatch):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    calls = {}

    def fake_add_well(backend, *, well_x, well_y, well_top, well_bottom, well_name, **kwargs):
        calls["backend"] = backend
        calls.setdefault("wells", []).append(
            {
                "well_x": well_x,
                "well_y": well_y,
                "well_top": well_top,
                "well_bottom": well_bottom,
                "well_name": well_name,
            }
        )
        calls["kwargs"] = kwargs

    monkeypatch.setattr(viewer_mod, "_add_well", fake_add_well)

    viewer = object.__new__(viewer_mod.PyVista3DViewer)
    viewer.theme = viewer_mod.PyVista3DViewerTheme(scale=(1.0, 1.0, 2.0))
    viewer.plotter = _DummyPlotter()
    viewer._pending_calls = []

    wells = [
        VerticalWell(name="W1", x=0.0, y=0.0, tops={"Top": 10.0, "Base": 20.0}),
        VerticalWell(name="W2", x=50.0, y=25.0, tops={"Top": 12.0, "Base": 22.0}),
    ]

    viewer.add_wells(
        wells,
        color="red",
        line_width=2.5,
        show_tops=True,
        label_top="Top",
    )

    viewer._render_queued()

    assert calls["backend"] is viewer.plotter
    assert len(calls["wells"]) == 2
    assert calls["wells"][0]["well_name"] == "W1"
    assert calls["wells"][1]["well_name"] == "W2"
    assert calls["kwargs"]["label_font_size"] == 15
    assert calls["kwargs"]["line_color"] == (1.0, 0.0, 0.0)
    assert calls["kwargs"]["label_color"] == (1.0, 0.0, 0.0)
    assert calls["kwargs"]["line_width"] == 2.5
    assert calls["kwargs"]["show_tops"] is True
    assert calls["kwargs"]["label_top"] == "Top"


def test_apply_camera_uses_camera_position_and_zoom(monkeypatch):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    class DummyCamera:
        def __init__(self):
            self.zoom_calls = []

        def zoom(self, factor):
            self.zoom_calls.append(factor)

    class DummyPlotter:
        def __init__(self):
            self.calls = []
            self.camera = DummyCamera()
            self.camera_position = None

        def reset_camera(self):
            self.calls.append("reset_camera")

        def reset_camera_clipping_range(self):
            self.calls.append("reset_camera_clipping_range")

    viewer = object.__new__(viewer_mod.PyVista3DViewer)
    viewer.plotter = DummyPlotter()

    camera = viewer_mod.Camera3D.isometric_se().with_zoom(2.0)

    viewer._apply_camera(camera, viewer.plotter)

    assert viewer.plotter.calls == [
        "reset_camera",
        "reset_camera_clipping_range",
        "reset_camera",
        "reset_camera_clipping_range",
    ]
    assert viewer.plotter.camera_position == [
        camera.position,
        camera.focal_point,
        camera.view_up,
    ]
    assert viewer.plotter.camera.zoom_calls == [2.0]


def test_viewer3d_screenshot_uses_cached_state_and_explicit_size(monkeypatch, tmp_path):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    monkeypatch.setattr(viewer_mod.pv, "Plotter", _DummyPlotter)

    viewer = object.__new__(viewer_mod.PyVista3DViewer)
    viewer.theme = viewer_mod.PyVista3DViewerTheme()
    viewer.camera = viewer_mod.Camera3D.isometric_se()
    viewer._point_labels = []
    viewer._meshes = []
    viewer._lines = []
    viewer._pending_calls = []
    viewer._scene_title = None
    viewer._cached_camera = "cached-camera"
    viewer._cached_window_size = (800, 600)

    output_path = tmp_path / "screenshot.png"

    viewer.screenshot(str(output_path), transparent=True, width=1024, height=768)

    assert viewer.plotter.off_screen is True
    assert viewer.plotter.screenshot_calls == [(str(output_path), (1024, 768))]
    assert viewer.plotter.background_color == (1, 1, 1, 0)
    assert viewer.plotter.camera == "cached-camera"


def test_viewer3d_screenshot_works_after_show(monkeypatch, tmp_path):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    monkeypatch.setattr(viewer_mod.pv, "Plotter", _DummyPlotter)

    viewer = viewer_mod.PyVista3DViewer()
    viewer.plotter.add_mesh("mesh")

    viewer.show(title="Scene")

    assert viewer._cached_window_size == (800, 600)
    assert viewer._cached_camera == "cached-camera"

    output_path = tmp_path / "after-show.png"

    viewer.screenshot(str(output_path))

    assert viewer.plotter.off_screen is True
    assert viewer.plotter.screenshot_calls == [(str(output_path), (800, 600))]


def test_viewer3d_plotter_close_caches_window_state(monkeypatch):
    pytest.importorskip("pyvista")

    import petres.viewers.viewer3d.pyvista.viewer as viewer_mod

    monkeypatch.setattr(viewer_mod.pv, "Plotter", _DummyPlotter)

    viewer = object.__new__(viewer_mod.PyVista3DViewer)
    viewer.theme = viewer_mod.PyVista3DViewerTheme()
    viewer.camera = viewer_mod.Camera3D.isometric_se()
    viewer._point_labels = []
    viewer._meshes = []
    viewer._scene_title = None
    viewer._cached_camera = None
    viewer._cached_window_size = None

    viewer.set_plotter()

    viewer.plotter.iren.interactor.observers["ExitEvent"](None, None)

    assert viewer._cached_window_size == (800, 600)
    assert viewer._cached_camera == "cached-camera"
