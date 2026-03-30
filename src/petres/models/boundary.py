from __future__ import annotations

from typing import Any, Sequence, Literal
from dataclasses import dataclass, field
from shapely.geometry import Polygon
from shapely import points, contains
from numpy.typing import ArrayLike
import numpy as np


@dataclass(frozen=True)
class BoundaryPolygon:
    """
    Represent a 2D area-of-interest boundary as a closed polygon in XY space.

    The class stores validated polygon vertices and a cached Shapely polygon
    object used for geometric operations such as point-in-polygon queries.

    Parameters
    ----------
    vertices : numpy.typing.ArrayLike
        Polygon vertices with shape ``(N, 2)``. The ring is automatically closed
        if the first and last points are not equal within tolerance.
    name : str or None, default=None
        Optional boundary label.

    Raises
    ------
    ValueError
        Raised during initialization when vertices cannot form a valid finite
        polygon.

    Notes
    -----
    Initialization validates vertex shape, enforces finite coordinates, closes
    the ring, and constructs an internal Shapely ``Polygon``.
    """

    vertices: ArrayLike
    name: str | None = None

    _polygon: Polygon = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate vertices, close the ring, and build the internal polygon.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If fewer than three unique points are provided or the polygon is
            invalid (self-intersections, degenerate ring).
        """
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
        """Return the axis-aligned bounding box of the boundary polygon.

        Parameters
        ----------
        None

        Returns
        -------
        tuple of float
            Bounding box in the form ``(xmin, ymin, xmax, ymax)``.
        """
        xy = self.vertices
        xmin = float(np.min(xy[:, 0]))
        ymin = float(np.min(xy[:, 1]))
        xmax = float(np.max(xy[:, 0]))
        ymax = float(np.max(xy[:, 1]))
        return xmin, ymin, xmax, ymax

    def contains(self, xy: ArrayLike) -> np.ndarray:
        """Vectorized point-in-polygon test using Shapely 2.x.

        Parameters
        ----------
        xy : numpy.typing.ArrayLike
            Candidate points of shape ``(N, 2)``.

        Returns
        -------
        ndarray of bool
            Boolean mask indicating whether each point lies inside the polygon.

        Raises
        ------
        ValueError
            If ``xy`` is not a 2D array with two columns.
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
        vertices: ArrayLike,
        *,
        name: str | None = None,
    ) -> "BoundaryPolygon":
        """
        Create a boundary polygon from raw vertices.

        Parameters
        ----------
        vertices : numpy.typing.ArrayLike
            Sequence of (x, y) coordinate pairs.
        name : str or None, optional
            Optional label for the polygon.

        Returns
        -------
        BoundaryPolygon
            Constructed boundary instance.

        Examples
        --------
        >>> verts = [(0, 0), (100, 0), (100, 50), (0, 50)]
        >>> boundary = BoundaryPolygon.from_vertices(verts, name="Field A")
        """
        return cls(vertices, name=name)

    @classmethod
    def from_xy(
        cls,
        x: Sequence[float],
        y: Sequence[float],
        *,
        name: str | None = None,
    ) -> "BoundaryPolygon":
        """
        Create a boundary polygon from separate x and y sequences.

        Parameters
        ----------
        x : Sequence[float]
            X-coordinates.
        y : Sequence[float]
            Y-coordinates; must match shape of `x`.
        name : str or None, optional
            Optional label for the polygon.

        Returns
        -------
        BoundaryPolygon
            Constructed boundary instance.

        Raises
        ------
        ValueError
            If `x` and `y` shapes differ.

        Examples
        --------
        >>> boundary = BoundaryPolygon.from_xy([0, 100, 100, 0], [0, 0, 50, 50], name="Box")
        """
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
        """
        Create an axis-aligned rectangular boundary from bounding box limits.

        Parameters
        ----------
        xmin, ymin : float
            Lower-left corner.
        xmax, ymax : float
            Upper-right corner; must satisfy xmax > xmin and ymax > ymin.
        name : str or None, optional
            Optional label for the polygon.

        Returns
        -------
        BoundaryPolygon
            Rectangular boundary instance.

        Raises
        ------
        ValueError
            If the bounds are invalid.

        Examples
        --------
        >>> boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 200.0, 150.0, name="AOI")
        """
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
        facecolor: str | tuple[Any, ...] = "#7ec8e3",
        edgecolor: str | tuple[Any, ...] = "#1f2937",
        linewidth: float = 1.8,
        alpha: float = 0.30,
        show_fill: bool = True,
        show_vertices: bool = False,
        vertex_size: float = 24.0,
        aspect: Literal["auto", "equal"] = "auto",
        title: str | None = None,
        **kwargs: Any,
    ) -> "Matplotlib2DViewer":
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
            Transparency of the fill (0-1).
        show_fill : bool, default=True
            Whether to fill the polygon.
        show_vertices : bool, default=False
            Whether to show vertex markers.
        vertex_size : float, default=24.0
            Size of vertex markers.
        aspect : {"auto", "equal"}, default="auto"
            Axes aspect ratio used by the viewer theme.
        title : str or None, default=None
            Title of the plot. If ``None``, no title is shown.
        **kwargs : Any
            Additional keyword arguments passed to
            ``Matplotlib2DViewer.add_boundary_polygon``.

        Returns
        -------
        Matplotlib2DViewer
            Viewer instance with the polygon added and shown.

        Examples
        --------
        >>> boundary = BoundaryPolygon.from_bbox(0.0, 0.0, 100.0, 80.0)
        >>> viewer = boundary.show(title="Boundary")
        >>> type(viewer).__name__
        'Matplotlib2DViewer'
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