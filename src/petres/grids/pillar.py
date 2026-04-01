from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Self
import numpy as np


from .._validation import _validate_finite_float
from .sampling._vertices import _resolve_xy_vertices
from .sampling._validation import _validate_vertex_array



@dataclass
class PillarGrid:
    """Represent a structured pillar-based grid with lateral i-j topology.

    Parameters
    ----------
    pillar_top : numpy.ndarray
        Top endpoints of each pillar with shape ``(nj+1, ni+1, 3)``.
    pillar_bottom : numpy.ndarray
        Bottom endpoints of each pillar with shape ``(nj+1, ni+1, 3)``.

    Notes
    -----
    Each pillar is interpreted as a straight segment between corresponding
    top and bottom points. The i-j topology is inferred from array dimensions.
    """

    pillar_top: np.ndarray     # Shape (nj+1, ni+1, 3)
    pillar_bottom: np.ndarray  # Shape (nj+1, ni+1, 3)

    def __init__(self, pillar_top: np.ndarray, pillar_bottom: np.ndarray) -> None:
        """Initialize a pillar grid from top and bottom pillar endpoints.

        Parameters
        ----------
        pillar_top : numpy.ndarray
            Top endpoints of pillars with shape ``(nj+1, ni+1, 3)``.
        pillar_bottom : numpy.ndarray
            Bottom endpoints of pillars with shape ``(nj+1, ni+1, 3)``.

        Returns
        -------
        None
            This constructor stores arrays and triggers post-initialization
            validation.
        """
        self.pillar_top = pillar_top
        self.pillar_bottom = pillar_bottom
        self.__post_init__()

    def __post_init__(self) -> None:
        """Validate pillar array dimensionality and consistency.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If top and bottom arrays have different shapes, or if their shape is
            not compatible with ``(nj+1, ni+1, 3)``.
        """
        if self.pillar_top.shape != self.pillar_bottom.shape:
            raise ValueError(
                "pillar_top and pillar_bottom must have the same shape, "
                f"got {self.pillar_top.shape} and {self.pillar_bottom.shape}"
            )
        
        if self.pillar_top.ndim != 3 or self.pillar_top.shape[2] != 3:
            raise ValueError(
                f"pillar arrays must have shape (nj+1, ni+1, 3), "
                f"got {self.pillar_top.shape}"
            )

    # ----------------------------
    # Dimensions
    # ----------------------------

    @property
    def niv(self) -> int:
        """Return the number of pillar vertices in the i direction.

        Returns
        -------
        int
            Number of pillar vertices along i.
        """
        return self.pillar_top.shape[1]

    @property
    def njv(self) -> int:
        """Return the number of pillar vertices in the j direction.

        Returns
        -------
        int
            Number of pillar vertices along j.
        """
        return self.pillar_top.shape[0]

    @property
    def ni(self) -> int:
        """Return the number of cells in the i direction.

        Returns
        -------
        int
            Number of cells along i.
        """
        return self.niv - 1

    @property
    def nj(self) -> int:
        """Return the number of cells in the j direction.

        Returns
        -------
        int
            Number of cells along j.
        """
        return self.njv - 1

    @property
    def cell_shape(self) -> Tuple[int, int]:
        """Return the cell-array shape.

        Returns
        -------
        tuple[int, int]
            Cell shape as ``(nj, ni)``.
        """
        return (self.nj, self.ni)

    @property
    def vertex_shape(self) -> Tuple[int, int]:
        """Return the pillar-vertex array shape.

        Returns
        -------
        tuple[int, int]
            Vertex shape as ``(nj+1, ni+1)``.
        """
        return (self.njv, self.niv)

    def to_eclipse_coord(self) -> np.ndarray:
        """Convert pillar endpoints to Eclipse COORD layout.

        Returns
        -------
        numpy.ndarray
            Array with shape ``(nj+1, ni+1, 6)`` where the last dimension is
            ``(x_top, y_top, z_top, x_bottom, y_bottom, z_bottom)``.
        """
        return np.concatenate(
            (self.pillar_top, self.pillar_bottom),
            axis=2
        )
    
    @classmethod
    def from_eclipse_coord(cls, coord: np.ndarray) -> Self:
        """Create PillarGrid from Eclipse COORD array.

        Parameters
        ----------
        coord : numpy.ndarray
            COORD array storing pillar top and bottom points as
            ``(x_top, y_top, z_top, x_bottom, y_bottom, z_bottom)`` with shape
            ``(nj+1, ni+1, 6)``.

        Returns
        -------
        PillarGrid
            New pillar grid initialized from COORD data.

        Raises
        ------
        ValueError
            If ``coord`` is not a 3D array with trailing dimension length 6.

        Examples
        --------
        >>> coord = np.zeros((3, 4, 6), dtype=float)
        >>> grid = PillarGrid.from_eclipse_coord(coord)
        >>> grid.vertex_shape
        (3, 4)
        """
        coord = np.asarray(coord)

        if coord.ndim != 3 or coord.shape[2] != 6:
            raise ValueError(
                f"COORD array must have shape (nj+1, ni+1, 6); got {coord.shape}"
            )
        pillar_top = coord[:, :, :3].copy()
        pillar_bottom = coord[:, :, 3:].copy()
        return cls(pillar_top=pillar_top, pillar_bottom=pillar_bottom)


    # ------------------------------------------------------------------
    # Regular / rectilinear constructors
    # ------------------------------------------------------------------
    @classmethod
    def from_rectilinear(
        cls,
        *,
        x: np.ndarray,     # (ni+1,)
        y: np.ndarray,     # (nj+1,)
        z_top: float,
        z_bottom: float,
    ) -> "PillarGrid":
        """Create vertical pillars from rectilinear x and y vertex vectors.

        Parameters
        ----------
        x : numpy.ndarray
            One-dimensional x-vertex coordinates with shape ``(ni+1,)``.
        y : numpy.ndarray
            One-dimensional y-vertex coordinates with shape ``(nj+1,)``.
        z_top : float
            Constant top z-value used for all pillar tops.
        z_bottom : float
            Constant bottom z-value used for all pillar bottoms. Must be larger
            than ``z_top``.

        Returns
        -------
        PillarGrid
            Vertical pillar grid whose top and bottom endpoints are defined by
            the provided constant z-values.

        Raises
        ------
        ValueError
            If vertex arrays are invalid or if ``z_bottom <= z_top``.

        Notes
        -----
        This constructor creates a vertical pillar envelope. It does not define
        layer geometry or per-corner depth values.
        """
     
        x = _validate_vertex_array(x, "x")
        y = _validate_vertex_array(y, "y")
        z_top = _validate_finite_float(z_top, "z_top")
        z_bottom = _validate_finite_float(z_bottom, "z_bottom")

        if z_bottom <= z_top:
            raise ValueError("'z_bottom' must be greater than 'z_top'.")

        X, Y = np.meshgrid(x, y)  # (nj+1, ni+1)

        Zt = np.full_like(X, float(z_top), dtype=float)
        Zb = np.full_like(X, float(z_bottom), dtype=float)

        pillar_top = np.stack([X, Y, Zt], axis=2)      # (nj+1, ni+1, 3)
        pillar_bot = np.stack([X, Y, Zb], axis=2)
        return cls(pillar_top=pillar_top, pillar_bottom=pillar_bot)

    @classmethod
    def from_regular(
        cls,
        *,
        xlim: Optional[tuple[float, float]] = None,
        ylim: Optional[tuple[float, float]] = None,
        ni: Optional[int] = None,
        nj: Optional[int] = None,
        dx: Optional[float] = None,
        dy: Optional[float] = None,
        z_top: float = 0.0,
        z_bottom: float = 1.0,
    ) -> Self:
        """Construct a vertical pillar grid from bounding box and resolution.

        Parameters
        ----------
        xlim : tuple[float, float] or None, default None
            Inclusive x-limits for grid generation.
        ylim : tuple[float, float] or None, default None
            Inclusive y-limits for grid generation.
        ni : int or None, default None
            Number of cells along i when explicit counts are used.
        nj : int or None, default None
            Number of cells along j when explicit counts are used.
        dx : float or None, default None
            Cell size along x when spacing-based resolution is used.
        dy : float or None, default None
            Cell size along y when spacing-based resolution is used.
        z_top, z_bottom : float, default 0.0, 1.0
            Constant pillar end depths.

        Returns
        -------
        PillarGrid
            Grid with vertical pillars spanning the limits.

        Raises
        ------
        ValueError
            If the provided limit/resolution combination is inconsistent.

        Notes
        -----
        Vertex vectors are resolved by ``_resolve_xy_vertices`` and then passed
        to :meth:`from_rectilinear`.

        Examples
        --------
        >>> grid = PillarGrid.from_regular(
        ...     xlim=(0.0, 1000.0), ylim=(0.0, 500.0), ni=10, nj=5
        ... )
        >>> grid.cell_shape
        (5, 10)
        """
        xv, yv = _resolve_xy_vertices(
            xlim=xlim, ylim=ylim, ni=ni, nj=nj, dx=dx, dy=dy
        )
        return cls.from_rectilinear(x=xv, y=yv, z_top=z_top, z_bottom=z_bottom)

    
    
    # @classmethod
    # def from_rectilinear(
    #     cls,
    #     x: np.ndarray,  # Shape (ni+1,)
    #     y: np.ndarray,  # Shape (nj+1,)
    #     z_top: float,
    #     z_bottom: float,
    # ) -> Self:
    #     """Create PillarGrid from rectilinear coordinates."""
    #     ni = len(x) - 1
    #     nj = len(y) - 1

    #     # Create coordinate arrays
    #     x_grid, y_grid = np.meshgrid(x, y, indexing='ij')

    #     # Create pillar arrays
    #     pillar_top = np.stack([
    #         x_grid,
    #         y_grid,
    #         np.full_like(x_grid, z_top)
    #     ], axis=2)

    #     pillar_bottom = np.stack([
    #         x_grid,
    #         y_grid,
    #         np.full_like(x_grid, z_bottom)
    #     ], axis=2)

    #     return cls(pillar_top=pillar_top, pillar_bottom=pillar_bottom)

        
    # # ----------------------------
    # # Pillar geometry
    # # ----------------------------

    # def pillar_vector(self, j: int, i: int) -> np.ndarray:
    #     """Get direction vector of pillar (j, i).
        
    #     Args:
    #         j, i: Pillar indices
            
    #     Returns:
    #         np.ndarray: Vector from top to bottom of pillar, shape (3,)
    #     """
    #     return self.pillar_bottom[j, i] - self.pillar_top[j, i]

    # def interpolate_pillar(self, j: int, i: int, t: float) -> np.ndarray:
    #     """Interpolate point along pillar at parameter t.
        
    #     Args:
    #         j, i: Pillar indices
    #         t: Interpolation parameter (0 = top, 1 = bottom)
            
    #     Returns:
    #         np.ndarray: Point coordinates (x, y, z), shape (3,)
    #     """
    #     if not 0.0 <= t <= 1.0:
    #         raise ValueError(f"t must be in [0, 1], got {t}")
        
    #     return self.pillar_top[j, i] + t * self.pillar_vector(j, i)
    
    # def interpolate_at_z(self, j: int, i: int, z: float) -> np.ndarray:
    #     """Interpolate (x, y) coordinates along pillar at given z-depth.
        
    #     Args:
    #         j, i: Pillar indices
    #         z: Z-coordinate
            
    #     Returns:
    #         np.ndarray: Point coordinates (x, y, z), shape (3,)
    #     """
    #     z_top = self.pillar_top[j, i, 2]
    #     z_bottom = self.pillar_bottom[j, i, 2]
        
    #     # Handle degenerate case
    #     if abs(z_bottom - z_top) < 1e-10:
    #         point = self.pillar_top[j, i].copy()
    #         point[2] = z
    #         return point
        
    #     # Compute parameter t
    #     t = (z - z_top) / (z_bottom - z_top)
        
    #     return self.interpolate_pillar(j, i, t)

    # def is_vertical(self, j: int, i: int, tol: float = 1e-6) -> bool:
    #     """Check if pillar is vertical (x, y constant).
        
    #     Args:
    #         j, i: Pillar indices
    #         tol: Tolerance for verticality check
            
    #     Returns:
    #         bool: True if pillar is vertical within tolerance
    #     """
    #     top_xy = self.pillar_top[j, i, :2]
    #     bottom_xy = self.pillar_bottom[j, i, :2]
        
    #     return np.linalg.norm(bottom_xy - top_xy) < tol

    # def get_inclination(self, j: int, i: int) -> float:
    #     """Get inclination angle from vertical in degrees.
        
    #     Args:
    #         j, i: Pillar indices
            
    #     Returns:
    #         float: Angle in degrees (0° = vertical, 90° = horizontal)
    #     """
    #     vec = self.pillar_vector(j, i)
    #     vertical = abs(vec[2])
    #     lateral = np.linalg.norm(vec[:2])
        
    #     return np.degrees(np.arctan2(lateral, vertical))

    # # ----------------------------
    # # Constructors
    # # ----------------------------

    # @classmethod
    # def from_rectilinear(
    #     cls,
    #     x: np.ndarray,  # Shape (ni+1,)
    #     y: np.ndarray,  # Shape (nj+1,)
    #     z_top: float,
    #     z_bottom: float,
    # ) -> 'PillarGrid':
    #     """Create vertical pillar grid from rectilinear coordinates.
        
    #     Args:
    #         x: X-coordinates of pillars, shape (ni+1,)
    #         y: Y-coordinates of pillars, shape (nj+1,)
    #         z_top: Z-coordinate at top
    #         z_bottom: Z-coordinate at bottom
            
    #     Returns:
    #         PillarGrid with vertical pillars
    #     """
    #     yy, xx = np.meshgrid(y, x, indexing='ij')
        
    #     njv, niv = xx.shape
    #     pillar_top = np.zeros((njv, niv, 3))
    #     pillar_bottom = np.zeros((njv, niv, 3))
        
    #     pillar_top[:, :, 0] = xx
    #     pillar_top[:, :, 1] = yy
    #     pillar_top[:, :, 2] = z_top
        
    #     pillar_bottom[:, :, 0] = xx
    #     pillar_bottom[:, :, 1] = yy
    #     pillar_bottom[:, :, 2] = z_bottom
        
    #     return cls(pillar_top, pillar_bottom)

    # @classmethod
    # def from_arrays(
    #     cls,
    #     x: np.ndarray,  # Shape (ni+1, nj+1)
    #     y: np.ndarray,  # Shape (ni+1, nj+1)
    #     z_top: np.ndarray,     # Shape (ni+1, nj+1) or scalar
    #     z_bottom: np.ndarray,  # Shape (ni+1, nj+1) or scalar
    # ) -> 'PillarGrid':
    #     """Create pillar grid from coordinate arrays.
        
    #     Args:
    #         x: X-coordinates, shape (nj+1, ni+1)
    #         y: Y-coordinates, shape (nj+1, ni+1)
    #         z_top: Z at top (array or scalar)
    #         z_bottom: Z at bottom (array or scalar)
            
    #     Returns:
    #         PillarGrid instance
    #     """
    #     if x.shape != y.shape:
    #         raise ValueError("x and y must have the same shape")
        
    #     njv, niv = x.shape
        
    #     # Broadcast scalars
    #     if np.isscalar(z_top):
    #         z_top = np.full((njv, niv), z_top)
    #     if np.isscalar(z_bottom):
    #         z_bottom = np.full((njv, niv), z_bottom)
        
    #     pillar_top = np.stack([x, y, z_top], axis=-1)
    #     pillar_bottom = np.stack([x, y, z_bottom], axis=-1)
        
    #     return cls(pillar_top, pillar_bottom)

    # def __repr__(self) -> str:
    #     """String representation."""
    #     return f"PillarGrid(shape={self.cell_shape}, n_pillars={self.niv}×{self.njv})"
