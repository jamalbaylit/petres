from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("petres")
except PackageNotFoundError:
    __version__ = "0.0.0"




from ._utils._colors import register_cmap
from .config.colors import DEFAULT_CMAP, PETRES_COLORS

register_cmap(name=DEFAULT_CMAP, colors=PETRES_COLORS)