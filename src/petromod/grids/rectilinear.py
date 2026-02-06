from dataclasses import dataclass, field
import numpy as np

@dataclass
class Rectilinear2DGrid:
    """2D structured rectilinear grid with lazy-evaluated cell centers.

    Attributes:
        x_vertex (np.ndarray): 1D array of grid line coordinates along x (size ni+1)
        y_vertex (np.ndarray): 1D array of grid line coordinates along y (size nj+1)
        active (np.ndarray): Boolean mask of active cells (shape nj x ni)

    Properties:
        x_center, y_center: 1D arrays of cell centers
        xx_vertex, yy_vertex: 2D meshgrid of vertex coordinates
        xx_center, yy_center: 2D meshgrid of cell centers
    """ 

    x_vertex: np.ndarray   # Grid line coordinates (ni+1,)
    y_vertex: np.ndarray   # Grid line coordinates (nj+1,)
    active: np.ndarray     # Boolean mask (nj, ni)
    
    # --- cached 1D centers ---
    _x_center: np.ndarray = field(init=False, repr=False, default=None)
    _y_center: np.ndarray = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_vertex: np.ndarray = field(init=False, repr=False, default=None)
    _yy_vertex: np.ndarray = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_center: np.ndarray = field(init=False, repr=False, default=None)
    _yy_center: np.ndarray = field(init=False, repr=False, default=None)

    @property
    def cell_shape(self):
        """Number of cells along j and i (nj, ni)."""
        return (self.nj, self.ni)

    @property
    def vertex_shape(self):
        """Number of vertices along j and i (nj+1, ni+1)."""
        return (self.njv, self.niv)

    # ----------------------------
    # Derived sizes
    # ----------------------------

    @property
    def niv(self) -> int:
        """
        Number of vertices in the i-direction.

        This corresponds to the length of the x-vertex coordinate array.
        For a structured grid with ni cells in the i-direction,
        the number of vertices is niv = ni + 1.
        """
        return self.x_vertex.size


    @property
    def njv(self) -> int:
        """
        Number of vertices in the j-direction.

        This corresponds to the length of the y-vertex coordinate array.
        For a structured grid with nj cells in the j-direction,
        the number of vertices is njv = nj + 1.
        """
        return self.y_vertex.size


    @property
    def ni(self) -> int:
        """
        Number of cells in the i-direction.

        Cells are defined between consecutive vertices.
        Therefore, ni = niv - 1.
        """
        return self.niv - 1


    @property
    def nj(self) -> int:
        """
        Number of cells in the j-direction.

        Cells are defined between consecutive vertices.
        Therefore, nj = njv - 1.
        """
        return self.njv - 1


    # ----------------------------
    # Cell centers (1D)
    # ----------------------------
    @property
    def x_center(self) -> np.ndarray:
        if self._x_center is None:
            self._x_center = 0.5 * (self.x_vertex[:-1] + self.x_vertex[1:])
        return self._x_center

    @property
    def y_center(self) -> np.ndarray:
        if self._y_center is None:
            self._y_center = 0.5 * (self.y_vertex[:-1] + self.y_vertex[1:])
        return self._y_center

    @property
    def xx_vertex(self) -> np.ndarray:
        if self._xx_vertex is None:
            self._xx_vertex, self._yy_vertex =  self._build_mesh(self.x_vertex, self.y_vertex)
        return self._xx_vertex
    
    @property
    def yy_vertex(self) -> np.ndarray:
        if self._yy_vertex is None:
            self._xx_vertex, self._yy_vertex =  self._build_mesh(self.x_vertex, self.y_vertex)
        return self._yy_vertex
    
    @property
    def xx_center(self) -> np.ndarray:
        if self._xx_center is None:
            self._xx_center, self._yy_center =  self._build_mesh(self.x_center, self.y_center)
        return self._xx_center
    
    @property
    def yy_center(self) -> np.ndarray:
        if self._yy_center is None:
            self._xx_center, self._yy_center =  self._build_mesh(self.x_center, self.y_center)
        return self._yy_center


    # ----------------------------
    # Cell center mesh (2D)
    # ----------------------------
    def _build_mesh(self, x, y):
        yy, xx = np.meshgrid(
            y,
            x,
            indexing="ij"
        )
        return xx, yy
