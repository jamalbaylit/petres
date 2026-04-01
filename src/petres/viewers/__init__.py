from .viewer3d.pyvista.viewer import PyVista3DViewer
from .viewer3d.pyvista.theme import PyVista3DViewerTheme
from .viewer2d.matplotlib.viewer import Matplotlib2DViewer
from .viewer2d.matplotlib.theme import Matplotlib2DViewerTheme


Viewer3D = PyVista3DViewer
Viewer2D = Matplotlib2DViewer
Viewer2DTheme = Matplotlib2DViewerTheme
Viewer3DTheme = PyVista3DViewerTheme

__all__ = [
    "Viewer3D",
    "PyVista3DViewer",
    "Viewer2D",
    "Matplotlib2DViewer",
    "Viewer2DTheme",
    "Viewer3DTheme"
    "PyVista3DViewerTheme"
]