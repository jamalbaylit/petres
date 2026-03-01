from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import numpy as np

from ..pillar import PillarGrid
from ...model.zone import Zone


def _build_zcorn_from_zones(*, pillars: PillarGrid, zones: Sequence[Zone]) -> np.ndarray:
    """
    Build ECLIPSE-style ZCORN array of shape (2*nk, 2*nj, 2*ni)
    by stacking zone internal interfaces (Zone.levels) in stratigraphic order.
    
    This function is fully vectorized for performance.
    
    Parameters
    ----------
    pillars : PillarGrid
        Lateral pillar geometry defining the grid topology.
        Can be regular, rectilinear, or fully irregular.
    zones : Sequence[Zone]
        Zones in stratigraphic order (top to bottom).
        Each zone's base must match the next zone's top at shared boundaries.
    
    Returns
    -------
    np.ndarray
        ZCORN array of shape (2*nk, 2*nj, 2*ni) where:
        - nk = total number of layers across all zones
        - nj, ni = lateral dimensions from pillars
    
    Notes
    -----
    - Zone boundaries are shared: only one interface is created at each zone boundary
    - Each zone's internal layering (zone.levels) defines additional interfaces within that zone
    - The function samples horizon surfaces at pillar (x, y) locations to determine z-coordinates
    
    Example
    -------
    >>> pillars = PillarGrid.from_rectilinear(
    ...     x=np.linspace(0, 100, 11),
    ...     y=np.linspace(0, 100, 11),
    ...     z_top=0, z_bottom=100
    ... )
    >>> # Create zones with horizons...
    >>> zcorn = _build_zcorn_from_zones(pillars=pillars, zones=[zone1, zone2])
    """
    if not zones:
        raise ValueError("At least one zone is required.")
    
    # ----------------------------
    # 1. Extract pillar node coordinates
    # ----------------------------
    # Use pillar_top for (x, y) since pillars may be non-vertical
    # Shape: (nj+1, ni+1, 3) where last dim is (x, y, z)
    pillar_xy = pillars.pillar_top[:, :, :2]  # (nj+1, ni+1, 2)
    njp1, nip1 = pillar_xy.shape[:2]
    nj, ni = njp1 - 1, nip1 - 1
    
    # Flatten to (n_nodes, 2) for vectorized horizon sampling
    xy_nodes = pillar_xy.reshape(-1, 2)  # (n_nodes, 2)
    
    # ----------------------------
    # 2. Build all interface surfaces by sampling horizons
    # ----------------------------
    # Collect all unique interfaces (avoid duplicates at zone boundaries)
    Z_interfaces = []
    
    for iz, zone in enumerate(zones):
        # Sample top and base surfaces at all pillar nodes
        zt = zone.top.sample(xy_nodes).reshape(njp1, nip1)  # (nj+1, ni+1)
        zb = zone.base.sample(xy_nodes).reshape(njp1, nip1)  # (nj+1, ni+1)
        
        # Validate ordering (assuming depth increases downward)
        if np.any(zb < zt):
            raise ValueError(
                f"Zone '{zone.name}': base surface is above top surface at some locations. "
                "Check zone definition and horizon interpolation."
            )
        
        # Get normalized levels for this zone
        levels = np.asarray(zone.levels, dtype=float)
        
        # Skip first level (t=0.0) for all zones after the first
        # This avoids duplicate interfaces at zone boundaries
        if iz > 0:
            levels = levels[1:]
        
        # Vectorized interpolation: z = zt + t * (zb - zt)
        # Shape: (n_levels, nj+1, ni+1)
        dz = zb - zt  # (nj+1, ni+1)
        
        for t in levels:
            z_interface = zt + t * dz  # (nj+1, ni+1)
            Z_interfaces.append(z_interface)
    
    # Stack all interfaces: shape (n_interfaces, nj+1, ni+1)
    Z_interfaces = np.stack(Z_interfaces, axis=0)
    
    n_interfaces = Z_interfaces.shape[0]
    nk = n_interfaces - 1  # Number of layers
    
    if nk <= 0:
        raise ValueError(
            "Not enough interfaces to form layers. "
            f"Got {n_interfaces} interfaces, need at least 2."
        )
    
    # ----------------------------
    # 3. Pack into ECLIPSE ZCORN format (vectorized)
    # ----------------------------
    # ZCORN shape: (2*nk, 2*nj, 2*ni)
    # Each cell (k, j, i) has 8 corners stored in a specific pattern
    zcorn = np.empty((2*nk, 2*nj, 2*ni), dtype=float)
    
    # For each layer k, extract top and bottom interfaces
    for k in range(nk):
        ztop = Z_interfaces[k]      # (nj+1, ni+1)
        zbot = Z_interfaces[k + 1]  # (nj+1, ni+1)
        
        # Map node corners to ZCORN indices
        # Each cell (j, i) has 4 corners at each k-level
        # ZCORN indexing: [kz, 2*j + dj, 2*i + di] where dj, di ∈ {0, 1}
        
        # Vectorized corner assignment using advanced indexing
        # Top corners (kz = 2*k)
        zcorn[2*k, 0::2, 0::2] = ztop[:-1, :-1]  # (j, i) -> (j+0, i+0)
        zcorn[2*k, 0::2, 1::2] = ztop[:-1, 1:]   # (j, i) -> (j+0, i+1)
        zcorn[2*k, 1::2, 0::2] = ztop[1:, :-1]   # (j, i) -> (j+1, i+0)
        zcorn[2*k, 1::2, 1::2] = ztop[1:, 1:]    # (j, i) -> (j+1, i+1)
        
        # Bottom corners (kz = 2*k + 1)
        zcorn[2*k+1, 0::2, 0::2] = zbot[:-1, :-1]
        zcorn[2*k+1, 0::2, 1::2] = zbot[:-1, 1:]
        zcorn[2*k+1, 1::2, 0::2] = zbot[1:, :-1]
        zcorn[2*k+1, 1::2, 1::2] = zbot[1:, 1:]
    
    return zcorn