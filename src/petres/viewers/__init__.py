from .viewer3d.pyvista.viewer import PyVista3DViewer
from .viewer2d.matplotlib.viewer import Matplotlib2DViewer
from .viewer2d.matplotlib.theme import Matplotlib2DViewerTheme


Viewer3D = PyVista3DViewer
Viewer2D = Matplotlib2DViewer
Viewer2DTheme = Matplotlib2DViewerTheme

__all__ = [
    "Viewer3D",
    "PyVista3DViewer",
    "Viewer2D",
    "Matplotlib2DViewer",
    "Viewer2DTheme"
]