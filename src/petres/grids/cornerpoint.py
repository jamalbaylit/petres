from __future__ import annotations

from typing import Optional, Dict, Self, Tuple, Sequence
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

from .builders.cornerpoint import _build_zcorn_from_zones
from ..eclipse.grids.write import GRDECLWriter
from ..eclipse.grids.read import GRDECLReader
from .pillar import PillarGrid
from ..model.zone import Zone

@dataclass
class CornerPointGrid:
    """
    3D corner-point grid with explicit corner coordinates.
    
    Builds on a PillarGrid foundation by adding:
    - Vertical layering (k-direction)
    - Corner z-coordinates for each cell
    - Active/inactive cell masking
    - Cell properties (porosity, permeability, etc.)
    
    Attributes:
        pillars (PillarGrid): Lateral pillar geometry
        zcorn (np.ndarray): Z-coordinates at cell corners, shape (nk, nj, ni, 2, 2, 2)
                              Indices: [k, j, i, di, dj, dk] where di,dj,dk ∈ {0,1}
        active (Optional[np.ndarray]): Boolean mask of active cells, shape (nk, nj, ni).
                                       If None, all cells are considered active (memory efficient).
        properties (Dict): Cell properties (e.g., 'porosity', 'permeability_x')
    
    Example:
        >>> # Create from pillar grid
        >>> pillars = PillarGrid.from_rectilinear(
        ...     x=np.linspace(0, 100, 11),
        ...     y=np.linspace(0, 100, 11),
        ...     z_top=0, z_bottom=100
        ... )
        >>> zcorn = ...  # Define corner depths
        >>> grid = CornerPointGrid(pillars, zcorn)
        >>> print(grid.shape)  # (10, 10, 5)
    """
    
    pillars: PillarGrid
    zcorn: np.ndarray                     # Shape (2*nk, 2*nj, 2*ni)
    active: Optional[np.ndarray] = None      # Shape (nk, nj, ni), boolean, or None for all active
    properties: Dict[str, np.ndarray] = field(default_factory=dict)
    
    # Cached properties
    _cell_centers: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    _cell_volumes: Optional[np.ndarray] = field(init=False, repr=False, default=None)
    
    def __post_init__(self):
        """Validate dimensions."""
        nj, ni = self.pillars.cell_shape
        nk = self.zcorn.shape[0]//2
        
        expected_corner_shape = (2*nk, 2*nj, 2*ni)
        if self.zcorn.shape != expected_corner_shape:
            raise ValueError(
                f"zcorn shape {self.zcorn.shape} != expected {expected_corner_shape}"
            )
        
        # Initialize or validate active array
        expected_active_shape = (nk, nj, ni)
        if self.active is None:
            # Use broadcast for memory-efficient all-active representation
            self.active = np.broadcast_to(True, expected_active_shape)
        else:
            self.active = np.asarray(self.active, dtype=bool)

            if self.active.shape != expected_active_shape:
                raise ValueError(
                    f"active shape {self.active.shape} != expected {expected_active_shape}"
                )
        
        # Validate properties
        for name, values in self.properties.items():
            if values.shape != expected_active_shape:
                raise ValueError(
                    f"Property '{name}' shape {values.shape} != expected {expected_active_shape}"
                )




    # ----------------------------
    # Dimensions
    # ----------------------------

    @property
    def ni(self) -> int:
        """Number of cells in i-direction."""
        return self.pillars.ni

    @property
    def nj(self) -> int:
        """Number of cells in j-direction."""
        return self.pillars.nj

    @property
    def nk(self) -> int:
        """Number of cells in k-direction (layers)."""
        return self.zcorn.shape[0] // 2

    @property
    def shape(self) -> Tuple[int, int, int]:
        """Grid shape (nk, nj, ni)."""
        return (self.nk, self.nj, self.ni)

    @property
    def n_cells(self) -> int:
        """Total number of cells."""
        return self.nk * self.nj * self.ni

    @property
    def n_active(self) -> int:
        """Number of active cells."""
        return np.sum(self.active)

    @classmethod
    def from_grdecl(cls, path: str | Path) -> CornerPointGrid:
        # Local import avoids circular deps and keeps startup light

        data = GRDECLReader().read(path)  # returns raw arrays/spec, not a grid
        coord = data.coord
        zcorn = data.zcorn
        actnum = data.actnum
        
        pillars = PillarGrid.from_eclipse_coord(coord)
        return cls(pillars=pillars, zcorn=zcorn, active=actnum)

    def to_grdecl(self, path: str | Path):
        """Export grid to GRDECL format."""
        coord = self.pillars.to_eclipse_coord()
        zcorn = self.zcorn
        actnum = self.active.astype(int)
        writer = GRDECLWriter()
        writer.write(path=path, coord=coord, zcorn=zcorn, actnum=actnum)

    def show(self, show_inactive: bool = False):
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        viewer.add_grid(grid=self, show_inactive=show_inactive)
        viewer.show()
    
    @classmethod
    def from_zones(cls, *, pillars: PillarGrid, zones: Sequence[Zone]) -> Self:
        """Create CornerPointGrid from zones with gap detection.
        
        Parameters
        ----------
        pillars : PillarGrid
            Lateral pillar geometry
        zones : Sequence[Zone]
            Zones in stratigraphic order (top to bottom)
        
        Returns
        -------
        CornerPointGrid
            Grid with gap-filling cells marked as inactive (ACTNUM=0)
        """
        zcorn, actnum = _build_zcorn_from_zones(pillars=pillars, zones=zones)
        return cls(pillars=pillars, zcorn=zcorn, active=actnum)
    
    # # ----------------------------
    # # Cell geometry
    # # ----------------------------

    
    # # TEST
    # def zcorn_to_cell_corner_z8(zcorn_3d: np.ndarray) -> np.ndarray:
    #     """
    #     Convert ZCORN shaped (2*nk, 2*nj, 2*ni) to (nk, nj, ni, 8) with ordering:
    #     0: TOP    (i,   j)
    #     1: TOP    (i+1, j)
    #     2: TOP    (i,   j+1)
    #     3: TOP    (i+1, j+1)
    #     4: BOTTOM (i,   j)
    #     5: BOTTOM (i+1, j)
    #     6: BOTTOM (i,   j+1)
    #     7: BOTTOM (i+1, j+1)
    #     """
    #     if zcorn_3d.ndim != 3:
    #         raise ValueError(f"Expected 3D array (2*nk,2*nj,2*ni), got ndim={zcorn_3d.ndim}")

    #     nk2, nj2, ni2 = zcorn_3d.shape
    #     if (nk2 % 2) or (nj2 % 2) or (ni2 % 2):
    #         raise ValueError(f"All dimensions must be even, got {zcorn_3d.shape}")

    #     nk, nj, ni = nk2 // 2, nj2 // 2, ni2 // 2
    #     out = np.empty((nk, nj, ni, 8), dtype=zcorn_3d.dtype)

    #     z = zcorn_3d  # alias

    #     # Top (k-top = 0::2), Bottom (k-bot = 1::2)
    #     kt = z[0::2]
    #     kb = z[1::2]

    #     # ---- TOP face ----
    #     out[..., 0] = kt[:, 0::2, 0::2]  # (i,   j)
    #     out[..., 1] = kt[:, 0::2, 1::2]  # (i+1, j)
    #     out[..., 2] = kt[:, 1::2, 0::2]  # (i,   j+1)
    #     out[..., 3] = kt[:, 1::2, 1::2]  # (i+1, j+1)

    #     # ---- BOTTOM face ----
    #     out[..., 4] = kb[:, 0::2, 0::2]
    #     out[..., 5] = kb[:, 0::2, 1::2]
    #     out[..., 6] = kb[:, 1::2, 0::2]
    #     out[..., 7] = kb[:, 1::2, 1::2]
    #     return out
    



    # def get_cell_corners(self, k: int, j: int, i: int) -> np.ndarray:
    #     """Get 8 corner coordinates of cell (k, j, i).
        
    #     Returns corners in standard hexahedron ordering:
    #     - Corners 0-3: Bottom face (counter-clockwise from top view)
    #     - Corners 4-7: Top face (counter-clockwise from top view)
        
    #     Args:
    #         k, j, i: Cell indices
            
    #     Returns:
    #         np.ndarray: Shape (8, 3) corner coordinates
    #     """
    #     corners = np.zeros((8, 3))
        
    #     # Bottom face (dk=0)
    #     for idx, (di, dj) in enumerate([(0,0), (1,0), (1,1), (0,1)]):
    #         z = self.zcorn[k, j, i, di, dj, 0]
    #         corners[idx] = self.pillars.interpolate_at_z(j+dj, i+di, z)
        
    #     # Top face (dk=1)
    #     for idx, (di, dj) in enumerate([(0,0), (1,0), (1,1), (0,1)]):
    #         z = self.zcorn[k, j, i, di, dj, 1]
    #         corners[4+idx] = self.pillars.interpolate_at_z(j+dj, i+di, z)
        
    #     return corners

    # @property
    # def cell_centers(self) -> np.ndarray:
    #     """Cell centers (average of 8 corners).
        
    #     Returns:
    #         np.ndarray: Shape (nk, nj, ni, 3)
    #     """
    #     if self._cell_centers is None:
    #         centers = np.zeros((self.nk, self.nj, self.ni, 3))
            
    #         for k in range(self.nk):
    #             for j in range(self.nj):
    #                 for i in range(self.ni):
    #                     corners = self.get_cell_corners(k, j, i)
    #                     centers[k, j, i] = np.mean(corners, axis=0)
            
    #         self._cell_centers = centers
        
    #     return self._cell_centers

    # @property
    # def cell_volumes(self) -> np.ndarray:
    #     """Cell volumes.
        
    #     Returns:
    #         np.ndarray: Shape (nk, nj, ni)
    #     """
    #     if self._cell_volumes is None:
    #         volumes = np.zeros((self.nk, self.nj, self.ni))
            
    #         for k in range(self.nk):
    #             for j in range(self.nj):
    #                 for i in range(self.ni):
    #                     corners = self.get_cell_corners(k, j, i)
    #                     volumes[k, j, i] = self._hexahedron_volume(corners)
            
    #         self._cell_volumes = volumes
        
    #     return self._cell_volumes

    # @staticmethod
    # def _hexahedron_volume(corners: np.ndarray) -> float:
    #     """Compute hexahedron volume via tetrahedral decomposition."""
    #     center = np.mean(corners, axis=0)
        
    #     # 6 faces
    #     faces = [
    #         [0, 1, 2, 3],  # Bottom
    #         [4, 5, 6, 7],  # Top
    #         [0, 1, 5, 4],  # Front
    #         [2, 3, 7, 6],  # Back
    #         [0, 3, 7, 4],  # Left
    #         [1, 2, 6, 5],  # Right
    #     ]
        
    #     volume = 0.0
    #     for face in faces:
    #         # Split quad into 2 triangles
    #         for tri in [[0, 1, 2], [0, 2, 3]]:
    #             v0 = corners[face[tri[0]]]
    #             v1 = corners[face[tri[1]]]
    #             v2 = corners[face[tri[2]]]
                
    #             mat = np.column_stack([v1 - v0, v2 - v0, center - v0])
    #             volume += abs(np.linalg.det(mat)) / 6.0
        
    #     return volume

    # # ----------------------------
    # # Properties
    # # ----------------------------

    # def add_property(self, name: str, values: np.ndarray):
    #     """Add cell property.
        
    #     Args:
    #         name: Property name
    #         values: Property values, shape (nk, nj, ni)
    #     """
    #     if values.shape != self.shape:
    #         raise ValueError(f"Property shape {values.shape} != grid shape {self.shape}")
    #     self.properties[name] = values

    # def get_property(self, name: str) -> Optional[np.ndarray]:
    #     """Get cell property by name."""
    #     return self.properties.get(name)

    # # ----------------------------
    # # Active cells
    # # ----------------------------

    # def get_active_indices(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    #     """Get (k, j, i) indices of active cells."""
    #     return np.where(self.active)

    # def get_active_centers(self) -> np.ndarray:
    #     """Get cell centers for active cells only.
        
    #     Returns:
    #         np.ndarray: Shape (n_active, 3)
    #     """
    #     return self.cell_centers[self.active]

    # def get_active_volumes(self) -> np.ndarray:
    #     """Get volumes for active cells only.
        
    #     Returns:
    #         np.ndarray: Shape (n_active,)
    #     """
    #     return self.cell_volumes[self.active]

    # def get_active_property(self, name: str) -> Optional[np.ndarray]:
    #     """Get property for active cells only."""
    #     prop = self.get_property(name)
    #     if prop is None:
    #         return None
    #     return prop[self.active]

    # # ----------------------------
    # # Constructors
    # # ----------------------------

    # @classmethod
    # def from_layers(
    #     cls,
    #     pillars: PillarGrid,
    #     layer_z: np.ndarray,  # Shape (nk+1, nj, ni) - z at layer interfaces
    #     active: Optional[np.ndarray] = None,
    #     properties: Optional[Dict[str, np.ndarray]] = None,
    # ) -> 'CornerPointGrid':
    #     """Create grid from layer interface depths.
        
    #     Args:
    #         pillars: PillarGrid defining lateral geometry
    #         layer_z: Z-coordinates at layer interfaces, shape (nk+1, nj, ni)
    #         active: Boolean mask (default: all active)
    #         properties: Cell properties dict
            
    #     Returns:
    #         CornerPointGrid instance
    #     """
    #     ni, nj = pillars.cell_shape
    #     nk = layer_z.shape[0] - 1
        
    #     # Build zcorn from layer interfaces
    #     zcorn = np.zeros((nk, nj, ni, 2, 2, 2))
        
    #     for k in range(nk):
    #         for j in range(nj):
    #             for i in range(ni):
    #                 # Bottom (dk=0) - all 4 corners same z
    #                 zcorn[k, j, i, :, :, 0] = layer_z[k, j, i]
    #                 # Top (dk=1) - all 4 corners same z
    #                 zcorn[k, j, i, :, :, 1] = layer_z[k+1, j, i]
        
    #     # Keep active as None if not provided (memory efficient)
    #     if properties is None:
    #         properties = {}
        
    #     return cls(pillars, zcorn, active, properties)

    # @classmethod
    # def from_rectilinear(
    #     cls,
    #     x: np.ndarray,  # Shape (ni+1,)
    #     y: np.ndarray,  # Shape (nj+1,)
    #     z: np.ndarray,  # Shape (nk+1,)
    #     active: Optional[np.ndarray] = None,
    #     properties: Optional[Dict[str, np.ndarray]] = None,
    # ) -> 'CornerPointGrid':
    #     """Create rectilinear corner-point grid.
        
    #     Args:
    #         x: X-coordinates, shape (ni+1,)
    #         y: Y-coordinates, shape (nj+1,)
    #         z: Z-coordinates, shape (nk+1,)
    #         active: Boolean mask (default: all active)
    #         properties: Cell properties
            
    #     Returns:
    #         CornerPointGrid instance
    #     """
    #     # Create vertical pillars
    #     pillars = PillarGrid.from_rectilinear(x, y, z[0], z[-1])
        
    #     ni, nj = pillars.cell_shape
    #     nk = len(z) - 1
        
    #     # Uniform layer depths
    #     layer_z = np.zeros((nk + 1, nj, ni))
    #     for k in range(nk + 1):
    #         layer_z[k, :, :] = z[k]
        
    #     return cls.from_layers(pillars, layer_z, active, properties)

    # def __repr__(self) -> str:
    #     """String representation."""
    #     return (
    #         f"CornerPointGrid(shape={self.shape}, "
    #         f"n_active={self.n_active}/{self.n_cells}, "
    #         f"properties={list(self.properties.keys())})"
    #     )
    
