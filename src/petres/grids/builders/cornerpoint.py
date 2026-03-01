from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import numpy as np

from ...model.zone import Zone

def _build_zcorn_from_zones(*, pillars, zones: Sequence["Zone"]) -> np.ndarray:
    """
    Build ECLIPSE-style ZCORN array of shape (2*nk, 2*nj, 2*ni)
    by stacking zone internal interfaces (Zone.levels) in stratigraphic order.
    """
    # 1) Node coordinates
    # Expect node grids: shape (nj+1, ni+1)
    Xn, Yn = pillars.node_xy()  # <-- you implement this on PillarGrid
    njp1, nip1 = Xn.shape
    nj, ni = njp1 - 1, nip1 - 1

    xy_nodes = np.column_stack([Xn.ravel(), Yn.ravel()])  # (n_nodes, 2)

    # 2) Build all interfaces at nodes (avoid duplicates at zone boundaries)
    Z_ifaces = []
    for iz, zone in enumerate(zones):
        zt = zone.top.sample(xy_nodes).reshape(nj+1, ni+1)
        zb = zone.base.sample(xy_nodes).reshape(nj+1, ni+1)

        # Ensure ordering (depends on your sign convention; adjust if needed)
        # Here we assume depth increases downward: base >= top
        if np.any(zb < zt):
            raise ValueError(f"Zone '{zone.name}': base is above top at some locations.")

        lv = np.asarray(zone.levels, dtype=float)

        # For all but the first zone, drop the first level (0.0) to avoid duplicate interface
        if iz > 0:
            lv = lv[1:]

        for t in lv:
            Z_ifaces.append(zt + t * (zb - zt))

    Z_ifaces = np.stack(Z_ifaces, axis=0)  # (n_ifaces, nj+1, ni+1)

    # 3) Number of k layers equals number of interface intervals
    nk = Z_ifaces.shape[0] - 1
    if nk <= 0:
        raise ValueError("Not enough interfaces to form layers.")

    # 4) Pack into zcorn (2*nk, 2*nj, 2*ni)
    zcorn = np.empty((2*nk, 2*nj, 2*ni), dtype=float)

    for k in range(nk):
        ztop = Z_ifaces[k]
        zbot = Z_ifaces[k+1]

        # Optional: handle near-zero thickness pinchouts by collapsing or later ACTNUM logic
        # thickness_nodes = zbot - ztop

        for dj in (0, 1):
            for di in (0, 1):
                # node selection for corners
                node_slice = (slice(dj, dj+nj), slice(di, di+ni))
                # top corners
                zcorn[2*k + 0, 0+dj:2*nj:2, 0+di:2*ni:2] = ztop[node_slice]
                # bottom corners
                zcorn[2*k + 1, 0+dj:2*nj:2, 0+di:2*ni:2] = zbot[node_slice]

    return zcorn