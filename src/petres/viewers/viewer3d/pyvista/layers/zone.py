from __future__ import annotations

from typing import Any
import pyvista as pv
import numpy as np

from .....models.zone import Zone
from ....._utils._color import Color


# def _add_zone(
#     backend,
#     zone: Zone,
#     *,
#     x: np.ndarray,
#     y: np.ndarray,
#     name: str | None = None,
#     color: tuple[float, float, float] | None = None,       # str ("tan"), RGB tuple, hex, etc.
#     opacity: float | None = None,
#     show_edges: bool | None = None,
#     show_layers: bool = True,
#     **mesh_kwargs: Any,             # forward all other PyVista kwargs
# ) -> pv.StructuredGrid:
#     """
#     Add a Zone as a thin 3D volume (top & base) using StructuredGrid.

#     Users can control styling via:
#       - color / opacity / show_edges (common)
#       - **mesh_kwargs (any pv.add_mesh kwargs)
#     """
#     x = np.asarray(x, dtype=float).ravel()
#     y = np.asarray(y, dtype=float).ravel()
#     if x.ndim != 1 or y.ndim != 1:
#         raise ValueError("x and y must be 1D arrays.")

#     z_top = zone.top.to_grid(x, y)    # (ny, nx)
#     z_base = zone.base.to_grid(x, y)  # (ny, nx)

#     xx2, yy2 = np.meshgrid(x, y)

#     X = np.dstack([xx2, xx2])
#     Y = np.dstack([yy2, yy2])
#     Z = np.dstack([z_top, z_base])

#     grid = pv.StructuredGrid(X, Y, Z)

#     actor_name = name or f"zone:{zone.name}"

#     # Provide sane defaults *only if user didn't specify scalars or color*
    
#     color = Color(color).as_rgb()

#     # Apply common knobs (but do not override if user already set them in mesh_kwargs)
#     if color is not None and "color" not in mesh_kwargs:
#         mesh_kwargs["color"] = color
#     if opacity is not None and "opacity" not in mesh_kwargs:
#         mesh_kwargs["opacity"] = opacity
#     if show_edges is not None and "show_edges" not in mesh_kwargs:
#         mesh_kwargs["show_edges"] = show_edges

#     backend.plotter.add_mesh(grid, name=actor_name, **mesh_kwargs)
#     return grid





# def _add_zone(
#     backend,
#     zone: Zone,
#     *,
#     x: np.ndarray,
#     y: np.ndarray,
#     name: str | None = None,
#     color: tuple[float, float, float] | None = None,  # can also be str/hex/etc
#     opacity: float | None = None,
#     show_edges: bool | None = None,
#     show_layers: bool = True,
#     **mesh_kwargs: Any,
# ) -> pv.StructuredGrid | list[pv.StructuredGrid]:
#     """
#     Add a Zone as a thin 3D volume (top & base). If show_layers=True and the Zone
#     has internal levels, render each layer as a separate thin volume so the layer
#     boundaries are visible.
#     """
#     x = np.asarray(x, dtype=float).ravel()
#     y = np.asarray(y, dtype=float).ravel()
#     if x.ndim != 1 or y.ndim != 1:
#         raise ValueError("x and y must be 1D arrays.")

#     z_top = zone.top.to_grid(x, y)    # (ny, nx)
#     z_base = zone.base.to_grid(x, y)  # (ny, nx)

#     xx2, yy2 = np.meshgrid(x, y)      # (ny, nx)

#     actor_name = name or f"zone:{zone.name}"

#     # Provide sane defaults *only if user didn't specify scalars or color*
#     if "scalars" not in mesh_kwargs and color is None and "color" not in mesh_kwargs:
#         color = "tan"

#     # Apply common knobs (but do not override if user already set them in mesh_kwargs)
#     if color is not None and "color" not in mesh_kwargs:
#         mesh_kwargs["color"] = color
#     if opacity is not None and "opacity" not in mesh_kwargs:
#         mesh_kwargs["opacity"] = opacity
#     if show_edges is not None and "show_edges" not in mesh_kwargs:
#         mesh_kwargs["show_edges"] = show_edges

#     # Helper: z at normalized level t in [0, 1]
#     # (linear interpolation between top and base)
#     dz = (z_base - z_top)
#     def z_at(t: float) -> np.ndarray:
#         return z_top + float(t) * dz

#     # --- Case 1: show as one volume (existing behavior) ---
#     if (not show_layers) or zone.n_layers <= 1:
#         X = np.dstack([xx2, xx2])
#         Y = np.dstack([yy2, yy2])
#         Z = np.dstack([z_top, z_base])
#         grid = pv.StructuredGrid(X, Y, Z)
#         backend.plotter.add_mesh(grid, name=actor_name, **mesh_kwargs)
#         return grid

#     # --- Case 2: show each layer as its own thin volume (visible interfaces) ---
#     grids: list[pv.StructuredGrid] = []

#     # Small convenience: if user did not provide opacity at all, layered rendering
#     # tends to look nicer with some transparency.
#     local_kwargs = dict(mesh_kwargs)
#     if opacity is None and "opacity" not in local_kwargs:
#         local_kwargs["opacity"] = 0.5

#     levels = zone.levels  # tuple[float,...], starts 0 ends 1
#     for i in range(zone.n_layers):
#         t0 = levels[i]
#         t1 = levels[i + 1]

#         z0 = z_at(t0)
#         z1 = z_at(t1)

#         X = np.dstack([xx2, xx2])
#         Y = np.dstack([yy2, yy2])
#         Z = np.dstack([z0, z1])

#         grid_i = pv.StructuredGrid(X, Y, Z)
#         layer_name = f"{actor_name}:layer:{i+1}"

#         backend.plotter.add_mesh(grid_i, name=layer_name, **local_kwargs)
#         grids.append(grid_i)

#     return grids


def _add_zone(
    backend,
    zone: Zone,
    *,
    x: np.ndarray,
    y: np.ndarray,
    name: str | None = None,
    color: tuple[float, float, float] | str | None = None,
    opacity: float = 1,
    show_layers: bool = True,
    show_outline: bool = True,   # reinterpret as "outline boundary highlight"
    outline_color="black",
    outline_width=2,
    **mesh_kwargs,
) -> pv.StructuredGrid | list[pv.StructuredGrid]:
    """
    Add a Zone as a 3D volume (top & base). If show_layers=True and the zone has
    internal levels, add each layer as a separate thin volume so layer boundaries
    are visible.

    Important:
    - show_edges does NOT draw all mesh edges (no "grid wireframe").
      It draws an OUTLINE highlight only (outer sharp edges), via feature edges.
    """

    # ----------------------------
    # Validate & build common grids
    # ----------------------------
    x = np.asarray(x, dtype=float).ravel()
    y = np.asarray(y, dtype=float).ravel()
    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1D arrays.")

    z_top = zone.top.to_grid(x, y)    # (ny, nx)
    z_base = zone.base.to_grid(x, y)  # (ny, nx)

    xx2, yy2 = np.meshgrid(x, y)      # (ny, nx)

    actor_name = name or f"zone:{zone.name}"

    color = Color(color).as_rgb()

    assert isinstance(show_outline, bool), \
         f"'show_outline' must be a boolean. Got: {type(show_outline).__name__}"
    assert (isinstance(opacity, (int, float)) and 0 <= opacity <= 1), \
        f"'opacity' must be a number between 0 and 1. Got: {opacity}"
    assert isinstance(outline_width, (int, float)) and outline_width >= 0, \
        f"'outline_width' must be a non-negative number. Got: {outline_width}"


    # Backwards-friendly aliases (if user passes 'show_edges', map it to 'show_outline')
    # We intentionally do NOT forward 'show_edges' to the solid add_mesh call.
    if "show_edges" in mesh_kwargs:
        # User passed old parameter name - use it to control outline
        show_outline = mesh_kwargs.pop("show_edges")
    

    def _add_outline_edges(dataset: pv.DataSet, *, outline_name: str) -> None:
        """
        Draw only outer "sharp" edges (no internal triangulation edges).
        Works well for your thin-volume geometry.
        """
        surf = dataset.extract_surface(algorithm='dataset_surface')

        edges = surf.extract_feature_edges(
            boundary_edges=True,        # in case surface is open somewhere
            feature_edges=True,         # sharp outer edges
            manifold_edges=False,
            non_manifold_edges=False,
        )

        # If nothing is found (possible for very smooth surfaces), do nothing.
        if edges.n_cells == 0 and edges.n_points == 0:
            return

        backend.plotter.add_mesh(
            edges,
            name=outline_name,
            color=outline_color,
            line_width=outline_width,
            lighting=False,
            render_lines_as_tubes=True,  # nicer outline
        )

    # z at normalized level t in [0,1]
    dz = (z_base - z_top)

    def z_at(t: float) -> np.ndarray:
        return z_top + float(t) * dz

    # Pre-compute X and Y arrays (same for all layers)
    X_template = np.dstack([xx2, xx2])
    Y_template = np.dstack([yy2, yy2])

    # Base mesh kwargs: explicitly disable edges, set color and opacity
    base_mesh_kwargs = {
        "show_edges": False,  # No grid wireframe
        "style": "surface",   # Force surface rendering (not wireframe)
        "color": color,
        "opacity": opacity,
        **mesh_kwargs,  # User overrides
    }

    # ----------------------------
    # Case 1: one volume only
    # ----------------------------
    if (not show_layers) or zone.n_layers <= 1:
        Z = np.dstack([z_top, z_base])
        grid = pv.StructuredGrid(X_template, Y_template, Z)
        
        backend.plotter.add_mesh(grid, name=actor_name, **base_mesh_kwargs)

        if show_outline:
            _add_outline_edges(grid, outline_name=f"{actor_name}:outline")

        return grid

    # ----------------------------
    # Case 2: layered rendering (each layer is its own thin volume)
    # ----------------------------
    grids: list[pv.StructuredGrid] = []

    levels = zone.levels
    for i in range(zone.n_layers):
        t0 = float(levels[i])
        t1 = float(levels[i + 1])

        z0 = z_at(t0)
        z1 = z_at(t1)

        Z = np.dstack([z0, z1])

        grid_i = pv.StructuredGrid(X_template, Y_template, Z)
        layer_name = f"{actor_name}:layer:{i+1}"

        backend.plotter.add_mesh(grid_i, name=layer_name, **base_mesh_kwargs)

        if show_outline:
            # Outline per layer (if you prefer ONLY one outline for whole zone,
            # move this outside the loop and outline a single full-zone grid instead.)
            _add_outline_edges(grid_i, outline_name=f"{layer_name}:outline")

        grids.append(grid_i)

    return grids