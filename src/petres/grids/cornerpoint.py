from __future__ import annotations

from typing import Any, Optional, Dict, Self, Tuple, Sequence
from dataclasses import dataclass, field
from typing import Callable
from pathlib import Path
import numpy as np
import warnings




from ..grids.sampling._validation import _validate_vertex_array
from ..grids.sampling._vertices import _resolve_xyz_vertices
from .builders.cornerpoint import _build_zcorn_from_zones
from ..errors.property import MissingEclipseKeywordError
from ..errors.grid import UnsupportedGridAttributeError
from ..eclipse.grids.write import GRDECLWriter
from ..eclipse.grids.read import GRDECLReader
from .pillar import PillarGrid
from ..models.zone import Zone
from ..models.boundary import BoundaryPolygon
from ..grids.properties import GridProperties, GridProperty



@dataclass(frozen=True)
class GridAttributeSpec:
    name: str
    description: str
    resolver: Callable[["CornerPointGrid"], np.ndarray]
    aliases: tuple[str, ...] = ()


GRID_ATTRIBUTES = (
    GridAttributeSpec("x", "cell-center x coordinate", lambda g: g.cell_centers[..., 0]),
    GridAttributeSpec("y", "cell-center y coordinate", lambda g: g.cell_centers[..., 1]),
    GridAttributeSpec(
        "depth",
        "cell-center depth (positive downward)",
        lambda g: g.cell_centers[..., 2],
        aliases=("z",),
    ),
    GridAttributeSpec("top", "top depth of cell", lambda g: g._cell_top_depth()),
    GridAttributeSpec("bottom", "bottom depth of cell", lambda g: g._cell_bottom_depth()),
    GridAttributeSpec("thickness", "cell thickness", lambda g: g._cell_thickness()),
    GridAttributeSpec("active", "1 for active cells, 0 for inactive", lambda g: g.active.astype(int)),
)

GRID_ATTRIBUTE_BY_NAME = {spec.name: spec for spec in GRID_ATTRIBUTES}

GRID_ATTRIBUTE_BY_ALIAS = {
    alias: spec
    for spec in GRID_ATTRIBUTES
    for alias in (spec.name, *spec.aliases)
}

RESERVED_GRID_PROPERTY_NAMES = frozenset(GRID_ATTRIBUTE_BY_ALIAS)


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

    zone_index: Optional[np.ndarray] = None        # shape (nk, nj, ni), int
    zone_names: Dict[int, str] = field(default_factory=dict)
    
    _properties: Dict[str, GridProperty] = field(default_factory=dict, repr=False)
    
    def __post_init__(self):
        """Validate dimensions."""
        nj, ni = self.pillars.cell_shape
        nk = self.zcorn.shape[0]//2
        
        expected_corner_shape = (2*nk, 2*nj, 2*ni)
        expected_cell_shape = (nk, nj, ni)
        expected_active_shape = expected_cell_shape

        if self.zcorn.shape != expected_corner_shape:
            raise ValueError(
                f"zcorn shape {self.zcorn.shape} != expected {expected_corner_shape}"
            )
        
        # Initialize or validate active array
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
        for name, prop in self._properties.items():
            if not isinstance(prop, GridProperty):
                raise TypeError(
                    f"Property '{name}' must be a GridProperty, got {type(prop)}."
                )
            if prop.values.shape != expected_cell_shape:
                raise ValueError(
                    f"Property '{name}' shape {prop.values.shape} != expected {expected_cell_shape}"
                )
            if prop.grid is not self:
                raise ValueError(
                    f"Property '{name}' belongs to a different grid instance."
                )
            
        self.set_zones(zone_index=self.zone_index, zone_names=self.zone_names)
    
    def _zone_mask(self, zone: str | Zone) -> np.ndarray:
        if self.zone_index is None:
            raise ValueError("Grid has no zones defined.")
        zone_name = self._normalize_zone_name(zone)
        zone_id = self._get_zone_id_from_name(zone_name)
        return self.zone_index == zone_id

    def summary(self) -> str:
        nk, nj, ni = self.shape
        total_cells = self.n_cells
        active = self.n_active
        inactive = self.n_inactive

        active_pct = 100 * active / total_cells if total_cells else 0.0
        inactive_pct = 100.0 - active_pct

        prop_names = list(self._properties.keys())
        zone_names = list(self.zone_names.values()) if self.zone_names else []

        def fmt(items: list[str], max_items: int = 4) -> str:
            if not items:
                return "Not Defined"
            if len(items) <= max_items:
                return ", ".join(items)
            return f"{', '.join(items[:max_items])}, … (+{len(items) - max_items} more)"

        lines = [
            "Grid Summary",
            "════════════",
            f"Shape         : {nk}×{nj}×{ni} (k×j×i)",
            f"Cells         : {total_cells}",
            f"Active        : {active} ({active_pct:.2f}%)",
            f"Inactive      : {inactive} ({inactive_pct:.2f}%)",
            f"Properties    : {fmt(prop_names)}",
            f"Zones         : {fmt(zone_names)}",
        ]
        return "\n".join(lines)

    @staticmethod
    def _normalize_zone_name(zone: str | Zone) -> str:
        if isinstance(zone, Zone):
            return zone.name

        if not isinstance(zone, str):
            raise TypeError("`zone` must be str, or `Zone` instance.")

        return zone
    
    def _get_zone_id_from_name(self, name: str) -> int:
        if name not in self._zone_name_to_id:
            raise ValueError(f"Zone '{name}' not found in grid zones.")
        return self._zone_name_to_id[name]

    def set_zones(
        self,
        zone_index: np.ndarray | None,
        zone_names: dict[int, str] | None,
    ) -> None:
        """
        Assign zone membership to the grid.

        Parameters
        ----------
        zone_index : np.ndarray
            Integer array of shape (nk, nj, ni) assigning each cell to a zone.
            Convention:
                0  -> gap / undefined / unassigned
                >0 -> valid zone id
        zone_names : dict[int, str], optional
            Mapping from zone id to zone name.
            If not provided, names will be auto-generated as "Zone {id}".

        Raises
        ------
        ValueError
            If shapes mismatch, invalid ids are present, or names are inconsistent.
        """

        
        # ----------------------------
        # 1. Validate zone_index
        # ----------------------------
        if zone_index is None:
            if not zone_names:
                zone_names = {}
            else:
                raise ValueError("`zone_names` provided without `zone_index`.")
        else:
            try:
                zone_index = np.asarray(zone_index, dtype=np.int32)
            except Exception as e:
                raise TypeError(f"Failed to convert `zone_index` to numpy array: {e}") from e
            
            if zone_index.shape != self.shape:
                raise ValueError(
                    f"`zone_index` shape {zone_index.shape} != expected {self.shape}"
                )

            if np.any(zone_index < 0):
                raise ValueError("`zone_index` cannot contain negative values.")


            # Extract used zone IDs (exclude 0 = gap)
            unique_ids = np.unique(zone_index)
            unique_ids = unique_ids[unique_ids != 0]


            # ----------------------------
            # 2. Handle zone_names
            # ----------------------------
            if not zone_names:
                zone_names = {int(i): f"Zone {int(i)}" for i in unique_ids}

            else:
                # Ensure dict[int, str]
                if not isinstance(zone_names, dict):
                    raise ValueError("`zone_names` must be a dict[int, str].")

                if 0 in zone_names:
                    raise ValueError("Zone ID 0 is reserved for gaps and cannot be named.")
                
                # Convert keys to int
                zone_names = {int(k): str(v) for k, v in zone_names.items()}

                # ---- 2a. Check duplicate names ----
                names = list(zone_names.values())
                if len(names) != len(set(names)):
                    duplicates = {n for n in names if names.count(n) > 1}
                    raise ValueError(f"Duplicate zone names detected: {duplicates}")

                # ---- 2b. Check all used IDs have names except 0 (gap) ----
                missing = set(unique_ids) - set(zone_names.keys())
                missing.discard(0)  # Allow 0 (gap) to be unnamed

                if missing:
                    raise ValueError(
                        f"`zone_names` missing definitions for zone ids: {sorted(missing)}"
                    )

                # ---- 2c. Optional: warn about unused names ----
                unused = set(zone_names.keys()) - set(unique_ids)
                unused.discard(0)  # Allow 0 (gap) to be unused

                if unused:
                    warnings.warn(
                        f"Unused zone ids in `zone_names`: {sorted(unused)}",
                        UserWarning,
                    )

        # ----------------------------
        # 3. Assign
        # ----------------------------
        self.zone_index = zone_index
        self.zone_names = zone_names
        self._zone_name_to_id = {v: k for k, v in zone_names.items()}


    # ----------------------------
    # Dimensions
    # ----------------------------
    
    @property
    def properties(self) -> GridProperties:
        return GridProperties(self)

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
        return int(np.nansum(self.active))
    
    @property
    def n_inactive(self) -> int:
        """Number of inactive cells."""
        return self.n_cells - self.n_active
    
    @property
    def cell_centers(self) -> np.ndarray:
        """Cell centers (average of 8 corners).
        
        Returns:
            np.ndarray: Shape (nk, nj, ni, 3)
        """
        corners = self._compute_cell_corners()  # Shape (nk, nj, ni, 8, 3)
        cell_centers = np.mean(corners, axis=3)  # Average over 8 corners
        return cell_centers
    
    @property
    def cell_volumes(self) -> np.ndarray:
        """Cell volumes computed via hexahedral decomposition.
        
        Returns:
            np.ndarray: Shape (nk, nj, ni)
        """
        corners = self._compute_cell_corners()  # Shape (nk, nj, ni, 8, 3)
        
        # Decompose each hexahedron into 6 tetrahedra using diagonal 0-7
        # Tetrahedron volume formula: |det([v1-v0, v2-v0, v3-v0])| / 6
        # Corner ordering (from _compute_cell_corners):
        #   0-3: Top face (i,j), (i+1,j), (i,j+1), (i+1,j+1)
        #   4-7: Bottom face (i,j), (i+1,j), (i,j+1), (i+1,j+1)
        
        def tet_volume(v0, v1, v2, v3):
            """Compute signed volume of tetrahedron with vectorized arrays."""
            # v1-v0, v2-v0, v3-v0 form the edge vectors
            # Volume = det([v1-v0, v2-v0, v3-v0]) / 6
            a = v1 - v0
            b = v2 - v0
            c = v3 - v0
            # Compute determinant using scalar triple product: a · (b × c)
            cross = np.cross(b, c)
            det = np.sum(a * cross, axis=-1)
            return det / 6.0
        
        # Extract corners for each tetrahedron
        c0, c1, c2, c3 = corners[..., 0, :], corners[..., 1, :], corners[..., 2, :], corners[..., 3, :]
        c4, c5, c6, c7 = corners[..., 4, :], corners[..., 5, :], corners[..., 6, :], corners[..., 7, :]
        
        # Decompose into 6 tetrahedra using diagonal 0-7
        vol = np.zeros(corners.shape[:3])  # Shape (nk, nj, ni)
        vol += tet_volume(c0, c1, c3, c7)
        vol += tet_volume(c0, c1, c5, c7)
        vol += tet_volume(c0, c4, c5, c7)
        vol += tet_volume(c0, c2, c3, c7)
        vol += tet_volume(c0, c2, c6, c7)
        vol += tet_volume(c0, c4, c6, c7)
        
        # Take absolute value to handle orientation
        volumes = np.abs(vol)
        
        return volumes
    

    @classmethod
    def from_grdecl(
        cls, path: str | Path,
        *,
        use_actnum: bool = True
    ) -> CornerPointGrid:
        # Local import avoids circular deps and keeps startup light

        data = GRDECLReader().read(path, use_actnum=use_actnum)  # returns raw arrays/spec, not a grid
        coord = data.coord
        zcorn = data.zcorn
        actnum = data.actnum
        
        pillars = PillarGrid.from_eclipse_coord(coord)
        return cls(pillars=pillars, zcorn=zcorn, active=actnum)

    def to_grdecl(
        self, 
        path: str | Path, 
        *,
        properties: Optional[Sequence[str]] = None,
        include_actnum: bool = True,
    ) -> None:
        """Export grid to GRDECL format."""
        coord = self.pillars.to_eclipse_coord()
        zcorn = self.zcorn
        actnum = self.active.astype(int) if include_actnum else None
        writer = GRDECLWriter()
        if properties is None:
            properties = list(self._properties.keys())
        else:
            try:
                properties = tuple(properties)
            except Exception as e:
                raise TypeError(f"`properties` must be a sequence of property names.") from e
        
        property_values = []
        property_keywords = []
        for prop_name in properties:
            prop = self.properties[prop_name]
            eclipse_keyword = prop.eclipse_keyword
            if eclipse_keyword is None:
                raise MissingEclipseKeywordError(property_name=prop_name)
                
            property_values.append(prop.values)
            property_keywords.append(prop.eclipse_keyword)

        return writer.write(
            path=path, 
            coord=coord, 
            zcorn=zcorn, 
            actnum=actnum, 
            property_values=property_values, 
            property_keywords=property_keywords,
        )

    def show(
        self, 
        show_inactive: bool = False, 
        scalars: str | None = None,
        color: Any = 'tan', 
        cmap: Optional[str] = 'turbo', 
        **kwargs
    ) -> None:
        from ..viewers.viewer3d.pyvista.viewer import PyVista3DViewer
        viewer = PyVista3DViewer()
        scalars = self._resolve_source(scalars) if scalars is not None else None
        color = None if scalars is not None else color
        viewer.add_grid(grid=self, show_inactive=show_inactive, color=color, scalars=scalars, cmap=cmap, **kwargs)
        viewer.show()
    
    @classmethod
    def from_rectilinear(
        cls,
        x: np.ndarray,
        y: np.ndarray,
        z: np.ndarray
    ) -> Self:
        """Create a simple corner-point grid from rectilinear coordinates."""
        
        z = _validate_vertex_array(z, "z")
        pillars = PillarGrid.from_rectilinear(x=x, y=y, z_top=z[0], z_bottom=z[-1])
        
        # Create simple ZCORN with flat layers
        nj, ni = pillars.cell_shape
        nk = len(z) - 1

        # Naive loop version (for clarity)
        # zcorn = np.zeros((2*nk, 2*nj, 2*ni))
        # for k in range(nk):
        #     zcorn[2*k:2*k+2, :, :] = z[k:k+2][:, np.newaxis, np.newaxis]
        
        # Fully vectorized version (optimized)
        z_planes = np.empty(2 * nk, dtype=z.dtype)
        z_planes[0::2] = z[:-1]
        z_planes[1::2] = z[1:]

        zcorn = np.broadcast_to(
            z_planes[:, None, None],
            (2 * nk, 2 * nj, 2 * ni),
        ).copy()

        return cls(pillars=pillars, zcorn=zcorn)


    @classmethod
    def from_regular(
        cls,
        *,
        xlim: tuple[float, float] | None = None,
        ylim: tuple[float, float] | None = None,
        zlim: tuple[float, float] | None = None,
        ni: int | None = None,
        nj: int | None = None,
        nk: int | None = None,
        dx: float | None = None,
        dy: float | None = None,
        dz: float | None = None,
        ) -> Self:
        x, y, z = _resolve_xyz_vertices(
            xlim=xlim, ylim=ylim, zlim=zlim, ni=ni, nj=nj, nk=nk, dx=dx, dy=dy, dz=dz
        )
        return cls.from_rectilinear(x=x, y=y, z=z)

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
        zcorn, actnum, zone_index, zone_names = _build_zcorn_from_zones(pillars=pillars, zones=zones)
        return cls(pillars=pillars, zcorn=zcorn, active=actnum, zone_index=zone_index, zone_names=zone_names)
    
    def apply_boundary(self, boundary: BoundaryPolygon):
        """Apply boundary polygon mask to active cells.
        
        Cells whose centers fall outside the polygon boundary will be marked
        as inactive (ACTNUM=0).
        
        Parameters
        ----------
        boundary : BoundaryPolygon
            2D boundary polygon in XY plane
        
        Notes
        -----
        This modifies the active array in-place and clears cached properties.
        """
        # Get cell centers (nk, nj, ni, 3)
        centers = self.cell_centers
        
        # Extract XY coordinates and reshape to (n_cells, 2)
        nk, nj, ni = self.shape
        xy = centers[..., :2].reshape(-1, 2)  # Shape: (nk*nj*ni, 2)
        
        # Check which cells are inside the boundary
        inside_mask = boundary.contains(xy)  # Shape: (nk*nj*ni,)
        
        # Reshape back to grid dimensions
        inside_mask = inside_mask.reshape(nk, nj, ni)
        
        # Update active array: cells outside boundary become inactive
        # Need to create a writable copy if active is a broadcast array
        if not self.active.flags.writeable:
            self.active = np.array(self.active, dtype=bool)
        
        self.active &= inside_mask
        
    def _compute_cell_corners(self) -> np.ndarray:
        """Compute 3D coordinates of all 8 corners for each cell.
        
        Returns:
            np.ndarray: Shape (nk, nj, ni, 8, 3) where the 8 corners are ordered:
                0-3: Top face (k-layer top)
                4-7: Bottom face (k-layer bottom)
                Each face: (i,j), (i+1,j), (i,j+1), (i+1,j+1)
        """
        nk, nj, ni = self.shape
        corners = np.zeros((nk, nj, ni, 8, 3))
        
        # Extract z-coordinates for all 8 corners
        # Top face (layer k top)
        z_top_00 = self.zcorn[0::2, 0::2, 0::2]    # (nk, nj, ni) - pillar (j, i)
        z_top_10 = self.zcorn[0::2, 0::2, 1::2]    # pillar (j, i+1)
        z_top_01 = self.zcorn[0::2, 1::2, 0::2]    # pillar (j+1, i)
        z_top_11 = self.zcorn[0::2, 1::2, 1::2]    # pillar (j+1, i+1)
        
        # Bottom face (layer k bottom)
        z_bot_00 = self.zcorn[1::2, 0::2, 0::2]    # pillar (j, i)
        z_bot_10 = self.zcorn[1::2, 0::2, 1::2]    # pillar (j, i+1)
        z_bot_01 = self.zcorn[1::2, 1::2, 0::2]    # pillar (j+1, i)
        z_bot_11 = self.zcorn[1::2, 1::2, 1::2]    # pillar (j+1, i+1)
        
        # Get pillar endpoints
        pt = self.pillars.pillar_top    # Shape (nj+1, ni+1, 3)
        pb = self.pillars.pillar_bottom  # Shape (nj+1, ni+1, 3)
        
        # Interpolate along pillars for each corner
        # For each pillar, compute t = (z - z_top) / (z_bottom - z_top)
        # Then position = pillar_top + t * (pillar_bottom - pillar_top)
        
        def interpolate_pillar_at_z(pillar_top, pillar_bottom, z):
            """Interpolate pillar position at given z-coordinates."""
            z_top = pillar_top[..., 2:3]  # Keep dimension for broadcasting
            z_bot = pillar_bottom[..., 2:3]
            
            # Compute interpolation parameter
            dz = z_bot - z_top
            # Handle vertical pillars (avoid division by zero)
            t = np.where(np.abs(dz) > 1e-10, (z[..., np.newaxis] - z_top) / dz, 0.5)
            
            # Interpolate position
            pos = pillar_top + t * (pillar_bottom - pillar_top)
            # Override z with exact value
            pos[..., 2] = z
            return pos
        
        # Top face corners (indices 0-3)
        corners[:, :, :, 0, :] = interpolate_pillar_at_z(pt[:-1, :-1], pb[:-1, :-1], z_top_00)
        corners[:, :, :, 1, :] = interpolate_pillar_at_z(pt[:-1, 1:], pb[:-1, 1:], z_top_10)
        corners[:, :, :, 2, :] = interpolate_pillar_at_z(pt[1:, :-1], pb[1:, :-1], z_top_01)
        corners[:, :, :, 3, :] = interpolate_pillar_at_z(pt[1:, 1:], pb[1:, 1:], z_top_11)
        
        # Bottom face corners (indices 4-7)
        corners[:, :, :, 4, :] = interpolate_pillar_at_z(pt[:-1, :-1], pb[:-1, :-1], z_bot_00)
        corners[:, :, :, 5, :] = interpolate_pillar_at_z(pt[:-1, 1:], pb[:-1, 1:], z_bot_10)
        corners[:, :, :, 6, :] = interpolate_pillar_at_z(pt[1:, :-1], pb[1:, :-1], z_bot_01)
        corners[:, :, :, 7, :] = interpolate_pillar_at_z(pt[1:, 1:], pb[1:, 1:], z_bot_11)
        
        return corners

    def _target_mask(
        self,
        zone: str | Zone | None = None,
        include_inactive: bool = False,
    ) -> np.ndarray:
        """
        Return boolean mask of target cells.
        """
        mask = np.ones(self.shape, dtype=bool)

        if not include_inactive:
            mask &= np.asarray(self.active, dtype=bool)

        if zone is not None:
            mask &= self._zone_mask(zone)

        return mask
    

    def _resolve_source(
        self,
        source: str | "GridProperty",
    ) -> np.ndarray:
        """
        Resolve one source to a full-grid ndarray.

        source can be:
        - built-in geometry source name
        - another GridProperty
        """
        if isinstance(source, str):
            if source in self._properties:
                prop = self._properties[source]
                return prop.values
            else:
                return self._get_attribute(source)

        if isinstance(source, GridProperty):
            if source.grid is not self:
                raise ValueError(
                    "Source GridProperty must belong to the same grid."
                )
            return source.values

        raise TypeError(
            "`source` entries must be either str or GridProperty."
        )
    
    def _get_attribute(self, name: str) -> np.ndarray:
        try:
            spec = GRID_ATTRIBUTE_BY_ALIAS[name]
        except KeyError as e:
            raise UnsupportedGridAttributeError(attribute_name=name, supported_names=GRID_ATTRIBUTE_BY_ALIAS.keys()) from e
        return spec.resolver(self)

            
    def __repr__(self) -> str:
        nk, nj, ni = self.shape
    
        return (
            f"{self.__class__.__name__}(shape=({nk}, {nj}, {ni}), "
            f"n_active={self.n_active}/{self.n_cells}, "
            f"properties={list(self._properties.keys())})"
        )
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


        
    
