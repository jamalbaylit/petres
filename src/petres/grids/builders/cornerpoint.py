from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np


from ..pillars import PillarGrid
from ...models.zone import Zone








# def _build_zcorn_from_zones(*, pillars: PillarGrid, zones: Sequence[Zone]) -> tuple[np.ndarray, np.ndarray]:
#     """
#     Build Eclipse-style ZCORN array of shape (2*nk, 2*nj, 2*ni)
#     by stacking zone internal interfaces (Zone.levels) in stratigraphic order.
    
#     This function is fully vectorized for performance.
    
#     Parameters
#     ----------
#     pillars : PillarGrid
#         Lateral pillar geometry defining the grid topology.
#         Can be regular, rectilinear, or fully irregular.
#     zones : Sequence[Zone]
#         Zones in stratigraphic order (top to bottom).
#         Zones can either share boundaries (zone[i].base == zone[i+1].top)
#         or have gaps between them. Gaps will create additional cells.
    
#     Returns
#     -------
#     tuple[np.ndarray, np.ndarray]
#         - ZCORN array of shape (2*nk, 2*nj, 2*ni) where:
#           - nk = total number of layers across all zones
#           - nj, ni = lateral dimensions from pillars
#         - ACTNUM array of shape (nk, nj, ni) where gap-filling cells are marked as inactive (0)
    
#     Notes
#     -----
#     - Shared boundaries: When zones share boundaries (zone[i].base ≈ zone[i+1].top),
#       only one interface is created at the boundary to avoid duplicates
#     - Gaps: When there's a gap between zones, both the base of the upper zone and
#       the top of the lower zone are included as separate interfaces, creating cells
#       that span the gap
#     - Each zone's internal layering (zone.levels) defines additional interfaces within that zone
#     - The function samples horizon surfaces at pillar (x, y) locations to determine z-coordinates
#     - Boundary detection uses a tolerance of 1e-6 for floating point comparison
    
#     Example
#     -------
#     >>> pillars = PillarGrid.from_rectilinear(
#     ...     x=np.linspace(0, 100, 11),
#     ...     y=np.linspace(0, 100, 11),
#     ...     z_top=0, z_bottom=100
#     ... )
#     >>> # Create zones with horizons...
#     >>> zcorn = _build_zcorn_from_zones(pillars=pillars, zones=[zone1, zone2])
#     """
#     assert isinstance(zones, Iterable), f"Expected iterable for zones. Got {type(zones)}."
#     assert len(zones) > 0, "At least one zone is required."
#     for zone in zones:
#         assert isinstance(zone, Zone), f"Expected Zone objects in zones. Got {type(zone)}."
#     assert isinstance(pillars, PillarGrid), f"Expected PillarGrid for pillars. Got {type(pillars)}."

#     # ----------------------------
#     # 1. Extract pillar node coordinates
#     # ----------------------------
#     # Use pillar_top for (x, y) since pillars may be non-vertical
#     # Shape: (nj+1, ni+1, 3) where last dim is (x, y, z)
#     pillar_xy = pillars.pillar_top[:, :, :2]  # (nj+1, ni+1, 2)
#     njp1, nip1 = pillar_xy.shape[:2]
#     nj, ni = njp1 - 1, nip1 - 1
    
#     # Flatten to (n_nodes, 2) for vectorized horizon sampling
#     xy_nodes = pillar_xy.reshape(-1, 2)  # (n_nodes, 2)
    
#     # ----------------------------
#     # 2. Build all interface surfaces by sampling horizons
#     # ----------------------------
#     # Collect all unique interfaces (handling both shared boundaries and gaps)
#     Z_interfaces = []
#     layer_is_active = []  # Track if each layer belongs to a zone (True) or gap (False)
#     # Note: When we add interface[N], we create layer[N-1] between interface[N-1] and interface[N]
    
#     for iz, zone in enumerate(zones):
#         # Sample top and base surfaces at all pillar nodes
#         zt = zone.top.sample(xy_nodes).reshape(njp1, nip1)  # (nj+1, ni+1)
#         zb = zone.base.sample(xy_nodes).reshape(njp1, nip1)  # (nj+1, ni+1)
        
#         # Validate ordering (assuming depth increases downward)
#         if np.any(zb < zt):
#             raise ValueError(
#                 f"Zone '{zone.name}': base surface is above top surface at some locations. "
#                 "Check zone definition and horizon interpolation."
#             )
        
#         # Get normalized levels for this zone
#         levels = list(np.asarray(zone.levels, dtype=float))
        
#         # Check if this zone shares a boundary with the previous zone
#         if iz > 0:
#             prev_base = Z_interfaces[-1]  # Last interface added
#             tolerance = 1e-6
#             zones_are_continuous = np.allclose(zt, prev_base, atol=tolerance, rtol=0)
            
#             if zones_are_continuous:
#                 # Shared boundary: skip first level to avoid duplicate interface
#                 levels = levels[1:]
#             else:
#                 # Gap exists: add top of current zone as new interface
#                 # This creates an INACTIVE gap layer between prev_base and zt
#                 Z_interfaces.append(zt.copy())
#                 layer_is_active.append(False)
#                 # Skip first level since we just added it
#                 levels = levels[1:]
        
#         # Add zone's internal interfaces
#         # Vectorized interpolation: z = zt + t * (zb - zt)
#         dz = zb - zt  # (nj+1, ni+1)
        
#         for t in levels:
#             z_interface = zt + t * dz  # (nj+1, ni+1)
#             Z_interfaces.append(z_interface)
            
#             # Every interface we add (except the very first one) creates a layer
#             # For zone interfaces, all layers are ACTIVE
#             if len(Z_interfaces) > 1:
#                 layer_is_active.append(True)
    
#     # Stack all interfaces: shape (n_interfaces, nj+1, ni+1)
#     Z_interfaces = np.stack(Z_interfaces, axis=0)
    
#     n_interfaces = Z_interfaces.shape[0]
#     nk = n_interfaces - 1  # Number of layers
    
#     if nk <= 0:
#         raise ValueError(
#             "Not enough interfaces to form layers. "
#             f"Got {n_interfaces} interfaces, need at least 2."
#         )
    
#     # ----------------------------
#     # 3. Pack into Eclipse ZCORN format (vectorized)
#     # ----------------------------
#     # ZCORN shape: (2*nk, 2*nj, 2*ni)
#     # Each cell (k, j, i) has 8 corners stored in a specific pattern
#     zcorn = np.empty((2*nk, 2*nj, 2*ni), dtype=float)
    
#     # For each layer k, extract top and bottom interfaces
#     for k in range(nk):
#         ztop = Z_interfaces[k]      # (nj+1, ni+1)
#         zbot = Z_interfaces[k + 1]  # (nj+1, ni+1)
        
#         # Map node corners to ZCORN indices
#         # Each cell (j, i) has 4 corners at each k-level
#         # ZCORN indexing: [kz, 2*j + dj, 2*i + di] where dj, di ∈ {0, 1}
        
#         # Vectorized corner assignment using advanced indexing
#         # Top corners (kz = 2*k)
#         zcorn[2*k, 0::2, 0::2] = ztop[:-1, :-1]  # (j, i) -> (j+0, i+0)
#         zcorn[2*k, 0::2, 1::2] = ztop[:-1, 1:]   # (j, i) -> (j+0, i+1)
#         zcorn[2*k, 1::2, 0::2] = ztop[1:, :-1]   # (j, i) -> (j+1, i+0)
#         zcorn[2*k, 1::2, 1::2] = ztop[1:, 1:]    # (j, i) -> (j+1, i+1)
        
#         # Bottom corners (kz = 2*k + 1)
#         zcorn[2*k+1, 0::2, 0::2] = zbot[:-1, :-1]
#         zcorn[2*k+1, 0::2, 1::2] = zbot[:-1, 1:]
#         zcorn[2*k+1, 1::2, 0::2] = zbot[1:, :-1]
#         zcorn[2*k+1, 1::2, 1::2] = zbot[1:, 1:]
    
#     # ----------------------------
#     # 4. Build ACTNUM array
#     # ----------------------------
#     # Convert layer_is_active list to a 3D boolean array (nk, nj, ni)
#     # If all layers are active, return None (more memory efficient)
#     if all(layer_is_active):
#         actnum = None
#     else:
#         actnum = np.ones((nk, nj, ni), dtype=bool)  # Start with all active
#         for k in range(nk):
#             if not layer_is_active[k]:
#                 actnum[k, :, :] = False  # Mark inactive gap layers
    
#     return zcorn, actnum





def _build_zcorn_from_zones(
    *,
    pillars: PillarGrid,
    zones: Sequence[Zone],
) -> tuple[np.ndarray, np.ndarray | None, np.ndarray, dict[int, str]]:
    """
    Build ZCORN, ACTNUM, and zone membership from stratigraphic zones.

    Parameters
    ----------
    pillars : PillarGrid
        Pillar geometry used to sample horizons and define cell topology.
    zones : Sequence[Zone]
        Non-empty ordered zones from top to bottom. Each zone must provide
        strictly increasing levels that start at 0.0 and end at 1.0.

    Returns
    -------
    tuple[np.ndarray, np.ndarray | None, np.ndarray, dict[int, str]]
        zcorn : np.ndarray
            Eclipse ZCORN array with shape (2*nk, 2*nj, 2*ni).
        actnum : np.ndarray | None
            Activity mask with shape (nk, nj, ni), or None when all layers are active.
        zone_index : np.ndarray
            Integer zone ids per cell with shape (nk, nj, ni). A value of 0 marks
            gap or unassigned layers.
        zone_names : dict[int, str]
            Mapping from positive zone id to zone name.

    Raises
    ------
    ValueError
        If zone geometry is invalid, levels are malformed, or there are not enough
        interfaces to form at least one layer.
    RuntimeError
        If internal layer metadata sizes become inconsistent.
    """
    assert isinstance(zones, Iterable), f"Expected iterable for zones. Got {type(zones)}."
    assert len(zones) > 0, "At least one zone is required."
    for zone in zones:
        assert isinstance(zone, Zone), f"Expected Zone objects in zones. Got {type(zone)}."
    assert isinstance(pillars, PillarGrid), f"Expected PillarGrid for pillars. Got {type(pillars)}."

    # ----------------------------
    # 1. Basic geometry
    # ----------------------------
    pillar_xy = pillars.pillar_top[:, :, :2]   # (nj+1, ni+1, 2)
    njp1, nip1 = pillar_xy.shape[:2]
    nj, ni = njp1 - 1, nip1 - 1

    xy_nodes = pillar_xy.reshape(-1, 2)        # (n_nodes, 2)

    # Zone ids: 1..N
    zone_names: dict[int, str] = {}
    zone_id_by_pos: list[int] = []

    for iz, zone in enumerate(zones, start=1):
        zone_names[iz] = zone.name
        zone_id_by_pos.append(iz)

    # ----------------------------
    # 2. Build interfaces + layer metadata
    # ----------------------------
    Z_interfaces: list[np.ndarray] = []
    layer_is_active: list[bool] = []
    layer_zone_ids: list[int] = []   # 0 for gap, >0 for actual zone

    tolerance = 1e-6

    for iz, zone in enumerate(zones):
        zone_id = zone_id_by_pos[iz]

        zt = zone.top.sample(xy_nodes).reshape(njp1, nip1)
        zb = zone.base.sample(xy_nodes).reshape(njp1, nip1)

        if np.any(zb < zt):
            raise ValueError(
                f"Zone '{zone.name}': base surface is above top surface at some locations. "
                "Check zone definition and horizon interpolation."
            )

        levels = np.asarray(zone.levels, dtype=float)
        if levels.ndim != 1:
            raise ValueError(f"Zone '{zone.name}': levels must be 1D.")
        if len(levels) < 2:
            raise ValueError(
                f"Zone '{zone.name}': levels must contain at least [0.0, 1.0]."
            )
        if not np.isclose(levels[0], 0.0):
            raise ValueError(f"Zone '{zone.name}': levels must start at 0.0.")
        if not np.isclose(levels[-1], 1.0):
            raise ValueError(f"Zone '{zone.name}': levels must end at 1.0.")
        if np.any(np.diff(levels) <= 0):
            raise ValueError(f"Zone '{zone.name}': levels must be strictly increasing.")

        # Handle continuity / gaps with previous zone
        if iz == 0:
            # First zone: add all interfaces
            levels_to_add = levels
        else:
            prev_base = Z_interfaces[-1]
            zones_are_continuous = np.allclose(zt, prev_base, atol=tolerance, rtol=0)

            if zones_are_continuous:
                # shared boundary already exists as previous base
                levels_to_add = levels[1:]
            else:
                # add current top explicitly -> creates a gap layer
                Z_interfaces.append(zt.copy())
                layer_is_active.append(False)
                layer_zone_ids.append(0)   # gap
                levels_to_add = levels[1:]

        dz = zb - zt

        for t in levels_to_add:
            z_interface = zt + t * dz
            Z_interfaces.append(z_interface)

            # Every new interface after the first creates one layer
            if len(Z_interfaces) > 1:
                layer_is_active.append(True)
                layer_zone_ids.append(zone_id)

    # ----------------------------
    # 3. Stack interfaces
    # ----------------------------
    Z_interfaces_arr = np.stack(Z_interfaces, axis=0)   # (n_interfaces, nj+1, ni+1)
    n_interfaces = Z_interfaces_arr.shape[0]
    nk = n_interfaces - 1

    if nk <= 0:
        raise ValueError(
            "Not enough interfaces to form layers. "
            f"Got {n_interfaces} interfaces, need at least 2."
        )

    if len(layer_is_active) != nk:
        raise RuntimeError("Internal error: layer_is_active length does not match nk.")
    if len(layer_zone_ids) != nk:
        raise RuntimeError("Internal error: layer_zone_ids length does not match nk.")

    # ----------------------------
    # 4. Pack ZCORN
    # ----------------------------
    zcorn = np.empty((2 * nk, 2 * nj, 2 * ni), dtype=float)

    for k in range(nk):
        ztop = Z_interfaces_arr[k]
        zbot = Z_interfaces_arr[k + 1]

        # top corners
        zcorn[2 * k,     0::2, 0::2] = ztop[:-1, :-1]
        zcorn[2 * k,     0::2, 1::2] = ztop[:-1, 1:]
        zcorn[2 * k,     1::2, 0::2] = ztop[1:, :-1]
        zcorn[2 * k,     1::2, 1::2] = ztop[1:, 1:]

        # bottom corners
        zcorn[2 * k + 1, 0::2, 0::2] = zbot[:-1, :-1]
        zcorn[2 * k + 1, 0::2, 1::2] = zbot[:-1, 1:]
        zcorn[2 * k + 1, 1::2, 0::2] = zbot[1:, :-1]
        zcorn[2 * k + 1, 1::2, 1::2] = zbot[1:, 1:]

    # ----------------------------
    # 5. Build ACTNUM
    # ----------------------------
    if all(layer_is_active):
        actnum = None
    else:
        actnum = np.ones((nk, nj, ni), dtype=bool)
        for k, is_active in enumerate(layer_is_active):
            if not is_active:
                actnum[k, :, :] = False

    # ----------------------------
    # 6. Build zone_index
    # ----------------------------
    zone_index = np.empty((nk, nj, ni), dtype=np.int32)
    for k, zone_id in enumerate(layer_zone_ids):
        zone_index[k, :, :] = zone_id

    return zcorn, actnum, zone_index, zone_names