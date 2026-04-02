"""2D viewer sub-package for petres.

Provides backend-agnostic and Matplotlib-specific 2D visualization components
for petroleum reservoir geometry.  Each backend sub-package exposes a concrete
viewer class and a matched theme dataclass built on top of the abstract
:class:`petres.viewers.viewer2d._core.base.Base2DViewer` interface.

Sub-packages
------------
_core
    Abstract base classes and protocols defining the 2D viewer contract.
matplotlib
    Matplotlib-backed 2D viewer and theme implementation.
"""

from __future__ import annotations
