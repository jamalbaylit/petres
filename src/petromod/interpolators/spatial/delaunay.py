from scipy.spatial import Delaunay
import matplotlib.pyplot as plt
import numpy as np

class DelaunayInterpolator:
    def __init__(self, field_data: FieldData, grid: StructuredGrid2D, z_values: np.ndarray):
        self.field_data = field_data
        tri = self._create_delaunay(
            field_data.well_x_coords,  
            field_data.well_y_coords
        )
        self.grid = grid
        self.simplex_ids = self._find_containing_triangles(tri, grid) # map grid → triangle ids
        self.weights = self._barycentric_weights(tri, self.simplex_ids, grid)

    def interpolate(
        self, 
        values:np.ndarray, 
    ):
        
        distribution = self._interpolate_on_triangles(
            self.tri,
            self.simplex_ids,
            self.weights,
            values,
            self.grid
        )
        return distribution

    def plot(self):
        return self._plot_delaunay(self.field_data.well_x_coords, self.field_data.well_y_coords)

    @staticmethod
    def _find_containing_triangles(tri, grid: StructuredGrid2D):
        pts = np.column_stack([
            grid.xx.ravel(),                              # (nx*ny,) flattened x-centers
            grid.yy.ravel()                               # (nx*ny,) flattened y-centers
        ])                                                # pts.shape == (nx*ny, 2)
                                                        # each row = one grid cell center

        simplex = tri.find_simplex(pts)                   # (nx*ny,)
                                                        # value = triangle index
                                                        # -1 means outside all triangles

        return simplex.reshape(grid.nx, grid.ny)          # back to grid shape (nx, ny)

    @staticmethod
    def _barycentric_weights(tri, simplex_ids, grid: StructuredGrid2D):
        nx, ny = grid.nx, grid.ny
        w = np.full((nx, ny, 3), np.nan)                  # store [w1, w2, w3] per cell

        mask = simplex_ids >= 0                           # True only for cells inside triangles

        pts = np.column_stack([
            grid.xx[mask],                                # x of valid grid cells
            grid.yy[mask]                                 # y of valid grid cells
        ])                                                # pts.shape == (N, 2)

        T = tri.transform[simplex_ids[mask]]              # (N, 3, 2)
                                                        # affine transform per triangle

        delta = pts - T[:, 2]                             # (x - x0, y - y0) per point

        bary12 = np.einsum(
            "ij,ijk->ik",                                 # vectorized dot product
            delta,                                        # (N, 2)
            T[:, :2]                                      # (N, 2, 2)
        )                                                  # bary12.shape == (N, 2)

        w1 = bary12[:, 0]                                 # first barycentric weight
        w2 = bary12[:, 1]                                 # second barycentric weight
        w3 = 1.0 - w1 - w2                                # third weight (sum = 1)

        w[mask, 0] = w1
        w[mask, 1] = w2
        w[mask, 2] = w3
        return w                                          # (nx, ny, 3)

    @staticmethod
    def _create_delaunay(x_coords, y_coords):
        points = np.column_stack([x_coords, y_coords])   # (n_wells, 2) → each row = [x, y]
        tri = Delaunay(points)                            # build triangles between wells
        return tri

    @staticmethod
    def _interpolate_on_triangles(
        tri,
        simplex_ids,
        weights,
        well_values,
        grid: StructuredGrid2D,
    ):

        z = np.full((grid.nx, grid.ny), np.nan)           # output surface

        mask = simplex_ids >= 0                           # only cells inside triangles

        tri_nodes = tri.simplices[simplex_ids[mask]]      # (N, 3)
                                                        # indices of wells per triangle

        z_nodes = well_values[tri_nodes]                  # (N, 3)
                                                        # z-values at triangle vertices

        z[mask] = np.sum(
            weights[mask] * z_nodes,                      # w1*z1 + w2*z2 + w3*z3
            axis=1
        )

        return z

    @staticmethod
    def _plot_delaunay(x_coords, y_coords):
        tri = DelaunayInterpolator._create_delaunay(x_coords, y_coords)

        fig, ax = plt.subplots(figsize=(10, 8))

        # ---- plot triangles ----
        ax.triplot(
            x_coords,
            y_coords,
            tri.simplices,
            color="gray",
            linewidth=0.8,
            alpha=0.8,
            zorder=1
        )

        # ---- plot well points ----
        ax.scatter(
            x_coords,
            y_coords,
            c="red",
            s=60,
            edgecolors="black",
            zorder=2,
            label="Wells"
        )

        # # ---- annotate wells ----
        # for name, x, y in zip(self.field_data.well_names(), x_coords, y_coords):
        #     ax.text(x, y, name, fontsize=8, ha="left", va="bottom")

        # # ---- plot boundary (optional) ----
        # if boundary_data is not None:
        #     ax.plot(
        #         boundary_data.x,
        #         boundary_data.y,
        #         "b-",
        #         linewidth=2.0,
        #         label="Boundary",
        #         zorder=3
        #     )

        ax.set_aspect("equal")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_title("Delaunay Triangulation (Well Control)")
        ax.grid(True, alpha=0.3)
        ax.legend()

        plt.tight_layout()
        plt.show()

        return tri

