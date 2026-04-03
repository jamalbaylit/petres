from __future__ import annotations

from typing import Any
import numpy as np
import pyvista as pv

from ....._utils._color import Color
from .....grids import CornerPointGrid

def _add_corner_point_grid(
    backend: Any,
    grid: CornerPointGrid,
    show_inactive: bool = False,
    color: Color | None = None,
    scalars: np.ndarray | None = None,
    cmap: str | None = None,
    **kwargs: Any,
) -> pv.UnstructuredGrid:
    """
    Add a corner-point grid layer to the active PyVista plotter.

    Parameters
    ----------
    backend : Any
        Viewer backend exposing a PyVista ``plotter``.
    grid : CornerPointGrid
        Grid containing pillar coordinates, ZCORN values, and activity flags.
    show_inactive : bool, default=False
        Include inactive cells when ``True``.
    color : Color | None, default=None
        Solid mesh color when scalar coloring is disabled.
    scalars : numpy.ndarray | None, default=None
        Cell scalar values. When inactive cells are filtered, values are filtered
        with the same mask.
    cmap : str | None, default=None
        Colormap used for scalar rendering.
    **kwargs : Any
        Additional keyword arguments forwarded to ``plotter.add_mesh``.

    Returns
    -------
    pyvista.UnstructuredGrid
        Unstructured hexahedral mesh built from the corner-point grid.

    Raises
    ------
    ValueError
        If no active cells remain after filtering, or if scalar size does not
        match the number of rendered cells.
    """
    # Extract grid dimensions
    nk, nj, ni = grid.shape
    
    # ========================================================================
    # Build cell corner coordinates (vectorized)
    # ========================================================================
    cell_corners = _construct_cell_corners_vectorized(grid)  # Shape: (nk, nj, ni, 8, 3)
    
    # ========================================================================
    # Apply active cell filtering (vectorized - NO LOOPS!)
    # ========================================================================
    if grid.active is not None and not np.all(grid.active) and not show_inactive:
        # Filter inactive cells using boolean indexing
        active_mask = grid.active  # Shape: (nk, nj, ni)
        cell_corners = cell_corners[active_mask]  # Shape: (n_active, 8, 3)
        n_cells = cell_corners.shape[0]
        
        if n_cells == 0:
            raise ValueError("No active cells found in the grid")
        
    else:
        # All cells active - reshape from 4D to 2D
        n_cells = nk * nj * ni
        cell_corners = cell_corners.reshape(n_cells, 8, 3)
    
    # ========================================================================
    # Build PyVista mesh (vectorized)
    # ========================================================================
    mesh = _build_pyvista_mesh_vectorized(cell_corners, n_cells)
    

    # ========================================================================
    # Attach scalar values (optional)
    # ========================================================================
    if scalars is not None:
        scalars = np.asarray(scalars, dtype=float)

        # Handle active filtering consistency
        if grid.active is not None and not np.all(grid.active) and not show_inactive:
            scalars = scalars[grid.active]

        scalars = scalars.reshape(-1)

        if scalars.shape[0] != n_cells:
            raise ValueError(
                f"Scalars size {scalars.shape[0]} does not match number of cells {n_cells}"
            )

        mesh.cell_data["values"] = scalars
    
        backend.plotter.add_mesh(
            mesh,
            scalars="values",
            cmap=cmap or "turbo",   # default fallback
            show_edges=True,
            **kwargs
        )
    else:
        backend.plotter.add_mesh(
            mesh,
            color=Color(color).as_rgb() if color is not None else 'tan',
            show_edges=True,
            **kwargs
        )

    return mesh


def _construct_cell_corners_vectorized(grid: CornerPointGrid) -> np.ndarray:
    """
    Construct cell-corner coordinates with stride-based vectorization.

    Parameters
    ----------
    grid : CornerPointGrid
        Grid with corner depths and pillar top/bottom coordinates.

    Returns
    -------
    numpy.ndarray
        Array with shape ``(nk, nj, ni, 8, 3)`` containing VTK-ordered corner
        coordinates for each cell.
    """
    nk, nj, ni = grid.shape
    corners = np.empty((nk, nj, ni, 8, 3), dtype=np.float64)
    
    pillar_tops = grid.pillars.pillar_top      # (nj+1, ni+1, 3)
    pillar_bots = grid.pillars.pillar_bottom   # (nj+1, ni+1, 3)
    zcorn = grid.zcorn                      # (2*nk, 2*nj, 2*ni)
    
    # Split ZCORN into cell-top / cell-bottom k-faces
    zt = zcorn[0::2]   # (nk, 2*nj, 2*ni) — top of each cell (shallower)
    zb = zcorn[1::2]   # (nk, 2*nj, 2*ni) — bottom of each cell (deeper)
    
    # VTK hexahedron corners: (vtk_idx, di, dj, z_face)
    vtk_corners = [
        (0, 0, 0, zt),  (1, 1, 0, zt),  (2, 1, 1, zt),  (3, 0, 1, zt),
        (4, 0, 0, zb),  (5, 1, 0, zb),  (6, 1, 1, zb),  (7, 0, 1, zb),
    ]
    
    # Pillar slices for di/dj offsets: 0 → [:-1], 1 → [1:]
    ps = [slice(None, -1), slice(1, None)]
    
    for idx, di, dj, zface in vtk_corners:
        # Extract z-coords via stride-2 slicing (no index arrays!)
        z = zface[:, dj::2, di::2]                  # (nk, nj, ni)
        
        # Pillar endpoints for this corner
        tops = pillar_tops[ps[dj], ps[di]]          # (nj, ni, 3)
        bots = pillar_bots[ps[dj], ps[di]]          # (nj, ni, 3)
        
        # Interpolation parameter: t = (z - z_top) / (z_bot - z_top)
        dz = bots[..., 2] - tops[..., 2]            # (nj, ni)
        with np.errstate(divide='ignore', invalid='ignore'):
            t = np.where(
                np.abs(dz) < 1e-10,
                0.5,                                 # vertical pillar fallback
                (z - tops[..., 2]) / dz,
            )                                        # (nk, nj, ni)
        
        # Interpolate (x, y, z) along pillar, then overwrite z with exact ZCORN
        corners[:, :, :, idx, :] = tops + t[..., None] * (bots - tops)
        corners[:, :, :, idx, 2] = z
    
    return corners


def _build_pyvista_mesh_vectorized(
    cell_corners: np.ndarray,
    n_cells: int,
) -> pv.UnstructuredGrid:
    """
    Build an unstructured hexahedral mesh from flattened cell corners.

    Parameters
    ----------
    cell_corners : numpy.ndarray
        Corner coordinate array with shape ``(n_cells, 8, 3)``.
    n_cells : int
        Number of hexahedral cells represented in ``cell_corners``.

    Returns
    -------
    pyvista.UnstructuredGrid
        Mesh containing VTK hexahedron connectivity and point coordinates.
    """
    # ========================================================================
    # Create point array
    # ========================================================================
    # Flatten all corners into a single point list
    points = cell_corners.reshape(-1, 3)  # Shape: (n_cells * 8, 3)
    
    # ========================================================================
    # Create connectivity array (vectorized)
    # ========================================================================
    # For VTK, each cell is: [n_points, point_id_0, point_id_1, ..., point_id_n-1]
    # For hexahedra: [8, id0, id1, id2, id3, id4, id5, id6, id7]
    
    # Generate point indices for all cells at once
    base_indices = np.arange(0, n_cells * 8, 8)[:, None]  # Shape: (n_cells, 1)
    corner_offsets = np.arange(8)[None, :]                 # Shape: (1, 8)
    connectivity = base_indices + corner_offsets           # Shape: (n_cells, 8)
    
    # Prepend the count (8) to each row
    cell_sizes = np.full((n_cells, 1), 8, dtype=np.int64)  # Shape: (n_cells, 1)
    cells = np.hstack([cell_sizes, connectivity])          # Shape: (n_cells, 9)
    cells = cells.ravel()                                  # Shape: (n_cells * 9,)
    
    # ========================================================================
    # Create cell type array
    # ========================================================================
    # VTK_HEXAHEDRON = 12
    cell_types = np.full(n_cells, pv.CellType.HEXAHEDRON, dtype=np.uint8)
    
    # ========================================================================
    # Create PyVista mesh
    # ========================================================================
    mesh = pv.UnstructuredGrid(cells, cell_types, points)
    
    return mesh



