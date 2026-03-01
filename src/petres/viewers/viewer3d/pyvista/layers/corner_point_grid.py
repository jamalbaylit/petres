import numpy as np
import pyvista as pv

def _add_corner_point_grid(backend, grid):
    """
    Add a CornerPointGrid to the PyVista plotter using fully vectorized mesh construction.
    
    This function builds a PyVista UnstructuredGrid from a CornerPointGrid without any loops,
    using numpy array operations for maximum performance. It handles:
    - Active cell filtering
    - Hexahedral cell construction
    - Proper VTK connectivity
    
    Args:
        backend: PyVista backend instance with plotter
        grid: CornerPointGrid instance containing corner_z, pillars, and active arrays
        
    Raises:
        ValueError: If no active cells are found or if grid dimensions are invalid
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
    if grid.active is not None and not np.all(grid.active):
        # Filter inactive cells using boolean indexing
        active_mask = grid.active  # Shape: (nk, nj, ni)
        cell_corners = cell_corners[active_mask]  # Shape: (n_active, 8, 3)
        n_cells = cell_corners.shape[0]
        
        if n_cells == 0:
            raise ValueError("No active cells found in the grid")
        
        print(f"Active cells: {n_cells:,} / {nk*nj*ni:,} ({100*n_cells/(nk*nj*ni):.1f}%)")
    else:
        # All cells active - reshape from 4D to 2D
        n_cells = nk * nj * ni
        cell_corners = cell_corners.reshape(n_cells, 8, 3)
        print(f"Total cells: {n_cells:,} (all active)")
    
    # ========================================================================
    # Build PyVista mesh (vectorized)
    # ========================================================================
    mesh = _build_pyvista_mesh_vectorized(cell_corners, n_cells)
    
    # Add mesh to plotter
    backend.plotter.add_mesh(mesh, color='tan', show_edges=True)
    
    return mesh


def _construct_cell_corners_vectorized(grid):
    """
    Construct all cell corner coordinates using stride-2 slice extraction.
    
    Extracts z-coordinates from grid.corner_z (shape 2*nk, 2*nj, 2*ni) using
    stride-2 slicing (no index arrays), then interpolates x,y along pillars.
    
    Corner ordering (VTK hexahedron):
    
        VTK idx │ di  dj │ ZCORN k-slice  │ Pillar (j, i)
        ────────┼────────┼────────────────┼──────────────
          0     │  0   0 │ 0::2 (cell top)│ [:-1, :-1]
          1     │  1   0 │ 0::2           │ [:-1,  1:]
          2     │  1   1 │ 0::2           │ [ 1:,  1:]
          3     │  0   1 │ 0::2           │ [ 1:, :-1]
          4     │  0   0 │ 1::2 (cell bot)│ [:-1, :-1]
          5     │  1   0 │ 1::2           │ [:-1,  1:]
          6     │  1   1 │ 1::2           │ [ 1:,  1:]
          7     │  0   1 │ 1::2           │ [ 1:, :-1]
    
    Args:
        grid: CornerPointGrid instance
        
    Returns:
        np.ndarray: Cell corners, shape (nk, nj, ni, 8, 3)
    """
    nk, nj, ni = grid.shape
    corners = np.empty((nk, nj, ni, 8, 3), dtype=np.float64)
    
    pillar_tops = grid.pillars.pillar_top      # (nj+1, ni+1, 3)
    pillar_bots = grid.pillars.pillar_bottom   # (nj+1, ni+1, 3)
    zcorn = grid.corner_z                      # (2*nk, 2*nj, 2*ni)
    
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


def _build_pyvista_mesh_vectorized(cell_corners, n_cells):
    """
    Build PyVista UnstructuredGrid from cell corners using vectorized operations.
    
    Args:
        cell_corners: Array of shape (n_cells, 8, 3) containing corner coordinates
        n_cells: Number of cells
        
    Returns:
        pv.UnstructuredGrid: PyVista mesh
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



