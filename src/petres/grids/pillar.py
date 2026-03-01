from dataclasses import dataclass
from typing import Tuple
import numpy as np


@dataclass
class PillarGrid:
    """
    Structured pillar-based grid defining lateral (i-j) topology.

    The grid is defined by straight coordinate lines (pillars) connecting 
    a top point to a bottom point. Pillars are indexed in i-j index space.

    Attributes:
        pillar_top (np.ndarray): Top endpoints of pillars, shape (nj+1, ni+1, 3)
        pillar_bottom (np.ndarray): Bottom endpoints of pillars, shape (nj+1, ni+1, 3)
    
    Properties:
        ni, nj: Number of cells in i, j directions
        niv, njv: Number of pillar vertices in i, j directions
        cell_shape: Shape tuple (nj, ni) for cell arrays
        vertex_shape: Shape tuple (nj+1, ni+1) for pillar arrays
    
    Example:
        >>> # Create a 2×2 pillar grid
        >>> top = np.array([[[0,0,0], [1,0,0], [2,0,0]],
        ...                 [[0,1,0], [1,1,0], [2,1,0]],
        ...                 [[0,2,0], [1,2,0], [2,2,0]]])
        >>> bottom = top.copy()
        >>> bottom[:,:,2] = 100  # Set depth to 100
        >>> grid = PillarGrid(top, bottom)
        >>> print(grid.cell_shape)  # (2, 2)
    """

    pillar_top: np.ndarray     # Shape (nj+1, ni+1, 3)
    pillar_bottom: np.ndarray  # Shape (nj+1, ni+1, 3)

    def __post_init__(self):
        """Validate pillar arrays."""
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
        """Number of pillar vertices in i-direction."""
        return self.pillar_top.shape[1]

    @property
    def njv(self) -> int:
        """Number of pillar vertices in j-direction."""
        return self.pillar_top.shape[0]

    @property
    def ni(self) -> int:
        """Number of cells in i-direction."""
        return self.niv - 1

    @property
    def nj(self) -> int:
        """Number of cells in j-direction."""
        return self.njv - 1

    @property
    def cell_shape(self) -> Tuple[int, int]:
        """Shape of cell arrays (nj, ni)."""
        return (self.nj, self.ni)

    @property
    def vertex_shape(self) -> Tuple[int, int]:
        """Shape of pillar vertex arrays (nj+1, ni+1)."""
        return (self.njv, self.niv)

    def to_eclipse_coord(self) -> np.ndarray:
        """Return pillars in ECLIPSE COORD format (nj+1, ni+1, 6)."""
        return np.concatenate(
            (self.pillar_top, self.pillar_bottom),
            axis=2
        )
    
    @classmethod
    def from_eclipse_coord(cls, coord: np.ndarray) -> 'PillarGrid':
        """Create PillarGrid from ECLIPSE COORD array."""
        if coord.ndim != 3 or coord.shape[2] != 6:
            raise ValueError(f"COORD array must have shape (nj+1, ni+1, 6), got {coord.shape}")
        
        pillar_top = coord[:, :, :3]
        pillar_bottom = coord[:, :, 3:]
        return cls(pillar_top=pillar_top, pillar_bottom=pillar_bottom)

        
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
