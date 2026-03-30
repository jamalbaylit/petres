from __future__ import annotations

from typing import Any, Sequence, Literal, Optional
from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely import points, contains
from numpy.typing import ArrayLike
import numpy as np


@dataclass(frozen=True)
class BoundaryPolygon:
    """
    A 2D boundary (AOI / field outline) represented as a closed polygon in XY.

    Parameters
    ----------
    vertices
        Closed ring vertices as ndarray of shape (N, 2). The last point equals the first.
    name
        Optional label.
    """

    vertices: np.ndarray
    name: str | None = None

    _polygon: Polygon = field(init=False, repr=False)

    def __post_init__(self) -> None:
        xy = self._validate_vertices(self.vertices)
        xy = self._close_ring(xy)

        # Validate ring length after closing (needs >= 4 including closure)
        if xy.shape[0] < 4:
            raise ValueError("BoundaryPolygon requires at least 3 unique points.")

        _polygon = Polygon(xy)
        if not _polygon.is_valid:
            raise ValueError("BoundaryPolygon is not a valid polygon (self-intersection or invalid ring).")
        object.__setattr__(self, "_polygon", _polygon)
        object.__setattr__(self, "vertices", xy)


    @property
    def bounds(self) -> tuple[float, float, float, float]:
        xy = self.vertices
        xmin = float(np.min(xy[:, 0]))
        ymin = float(np.min(xy[:, 1]))
        xmax = float(np.max(xy[:, 0]))
        ymax = float(np.max(xy[:, 1]))
        return xmin, ymin, xmax, ymax

    def contains(self, xy: np.ndarray) -> np.ndarray:
        """
        Vectorized point-in-polygon using Shapely 2.x (GEOS backend).
        """
        pts = np.asarray(xy, dtype=float)
        if pts.ndim != 2 or pts.shape[1] != 2:
            raise ValueError("xy must be shape (N,2).")

        poly = self._polygon
        shp_points = points(pts[:, 0], pts[:, 1])

        return contains(poly, shp_points)

    # ----------------------------
    # Constructors
    # ----------------------------
    @classmethod
    def from_vertices(
        cls,
        vertices: Any,
        *,
        name: str | None = None,
    ) -> "BoundaryPolygon":
        return cls(vertices, name=name)

    @classmethod
    def from_xy(
        cls,
        x: Sequence[float],
        y: Sequence[float],
        *,
        name: str | None = None,
    ) -> "BoundaryPolygon":
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        if x.shape != y.shape:
            raise ValueError(f"x and y must have the same shape. Got {x.shape} vs {y.shape}.")
        vertices = np.column_stack([x, y])
        return cls.from_vertices(vertices, name=name)

    @classmethod
    def from_bbox(
        cls,
        xmin: float,
        ymin: float,
        xmax: float,
        ymax: float,
        *,
        name: str | None = None,
    ) -> "BoundaryPolygon":
        if not (xmin < xmax and ymin < ymax):
            raise ValueError("Invalid bbox: require xmin < xmax and ymin < ymax.")
        vertices = np.array(
            [
                [xmin, ymin],
                [xmax, ymin],
                [xmax, ymax],
                [xmin, ymax],
                [xmin, ymin],
            ],
            dtype=float,
        )
        return cls(vertices=vertices, name=name)

    def _validate_vertices(self, vertices: ArrayLike) -> np.ndarray:
        """
        Validate and normalize 2D polygon vertices.

        Parameters
        ----------
        vertices : ArrayLike
            Sequence of (x, y) coordinate pairs.

        Returns
        -------
        ndarray of shape (N, 2)
            Validated float64 array of vertices.

        Raises
        ------
        ValueError
            If shape is invalid or contains non-finite values.
        """
        try:
            arr = np.asarray(vertices, dtype=np.float64)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Failed to convert vertices to float array: {e}") from e

        if arr.ndim != 2 or arr.shape[1] != 2:
            raise ValueError(
                f"`vertices` must be array-like with shape (N, 2). "
                f"Got shape {arr.shape}."
            )

        if arr.shape[0] < 3:
            raise ValueError(
                f"`vertices` must contain at least 3 points. "
                f"Got {arr.shape[0]}."
            )

        if not np.isfinite(arr).all():
            raise ValueError("`vertices` must not contain NaN or infinite values.")

        return np.ascontiguousarray(arr)
    

    def _close_ring(self, xy: np.ndarray, *, tol: float = 1e-12) -> np.ndarray:
        """
        Ensure polygon ring is closed.

        Parameters
        ----------
        xy : ndarray of shape (N, 2)
            Vertex coordinates.
        tol : float, optional
            Numerical tolerance for closure check.

        Returns
        -------
        ndarray
            Closed ring (first point repeated at end if needed).
        """
        if np.allclose(xy[0], xy[-1], atol=tol):
            return xy
        return np.vstack((xy, xy[0]))
    
    def show(
        self,
        *,
        facecolor: str | tuple = "#7ec8e3",
        edgecolor: str | tuple = "#1f2937",
        linewidth: float = 1.8,
        alpha: float = 0.30,
        show_fill: bool = True,
        show_vertices: bool = False,
        vertex_size: float = 24.0,
        aspect: Literal["auto", "equal"] = "auto",
        title: Optional[str] = None,
        **kwargs,
    ):
        """
        Quick visualization of the boundary polygon using Matplotlib.

        Parameters
        ----------
        facecolor : str or tuple, default="#7ec8e3"
            Fill color of the polygon.
        edgecolor : str or tuple, default="#1f2937"
            Edge (border) color of the polygon.
        linewidth : float, default=1.8
            Width of the polygon boundary line.
        alpha : float, default=0.30
            Transparency of the fill (0–1).
        show_fill : bool, default=True
            Whether to fill the polygon.
        show_vertices : bool, default=False
            Whether to show vertex markers.
        vertex_size : float, default=24.0
            Size of vertex markers.
        title : str, optional
            Title of the plot. If None, no title is shown.
        **kwargs
            Additional arguments passed to the viewer.
        """

        from ..viewers.viewer2d.matplotlib.viewer import Matplotlib2DViewer
        from ..viewers.viewer2d.matplotlib.theme import Matplotlib2DViewerTheme

        viewer = Matplotlib2DViewer(
            theme=Matplotlib2DViewerTheme(aspect=aspect)
        )

        viewer.add_boundary_polygon(
            self,
            facecolor=facecolor,
            edgecolor=edgecolor,
            linewidth=linewidth,
            alpha=alpha,
            show_fill=show_fill,
            show_vertices=show_vertices,
            vertex_size=vertex_size,
            **kwargs,
        )

        viewer.show(title=title)
        return viewer