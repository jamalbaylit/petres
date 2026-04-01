from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Rectilinear2DGrid:
    """2D structured rectilinear grid with lazy-evaluated cell centers.

    Parameters
    ----------
    x_vertex : np.ndarray
        1D array of grid line coordinates along x, shape ``(ni+1,)``.
    y_vertex : np.ndarray
        1D array of grid line coordinates along y, shape ``(nj+1,)``.
    active : np.ndarray
        Boolean mask of active cells, shape ``(nj, ni)``.

    Notes
    -----
    Cell-center arrays and 2D meshgrids are computed lazily on first access
    and cached for subsequent calls.
    """

    x_vertex: np.ndarray   # Grid line coordinates (ni+1,)
    y_vertex: np.ndarray   # Grid line coordinates (nj+1,)
    active: np.ndarray     # Boolean mask (nj, ni)

    # --- cached 1D centers ---
    _x_center: np.ndarray | None = field(init=False, repr=False, default=None)
    _y_center: np.ndarray | None = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_vertex: np.ndarray | None = field(init=False, repr=False, default=None)
    _yy_vertex: np.ndarray | None = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_center: np.ndarray | None = field(init=False, repr=False, default=None)
    _yy_center: np.ndarray | None = field(init=False, repr=False, default=None)

    @property
    def cell_shape(self) -> tuple[int, int]:
        """Return the number of cells along j and i as ``(nj, ni)``."""
        return (self.nj, self.ni)

    @property
    def vertex_shape(self) -> tuple[int, int]:
        """Return the number of vertices along j and i as ``(nj+1, ni+1)``."""
        return (self.njv, self.niv)

    # ----------------------------
    # Derived sizes
    # ----------------------------

    @property
    def niv(self) -> int:
        """Return the number of vertices in the i-direction.

        This corresponds to the length of the x-vertex coordinate array.
        For a structured grid with ni cells in the i-direction,
        the number of vertices is niv = ni + 1.

        Returns
        -------
        int
            Number of vertices along the i-axis.
        """
        return self.x_vertex.size

    @property
    def njv(self) -> int:
        """Return the number of vertices in the j-direction.

        This corresponds to the length of the y-vertex coordinate array.
        For a structured grid with nj cells in the j-direction,
        the number of vertices is njv = nj + 1.

        Returns
        -------
        int
            Number of vertices along the j-axis.
        """
        return self.y_vertex.size

    @property
    def ni(self) -> int:
        """Return the number of cells in the i-direction.

        Cells are defined between consecutive vertices.
        Therefore, ni = niv - 1.

        Returns
        -------
        int
            Number of cells along the i-axis.
        """
        return self.niv - 1

    @property
    def nj(self) -> int:
        """Return the number of cells in the j-direction.

        Cells are defined between consecutive vertices.
        Therefore, nj = njv - 1.

        Returns
        -------
        int
            Number of cells along the j-axis.
        """
        return self.njv - 1

    # ----------------------------
    # Cell centers (1D)
    # ----------------------------

    @property
    def x_center(self) -> np.ndarray:
        """Return the 1D array of cell-center x-coordinates.

        Computed as the midpoint between consecutive x-vertices. The result
        is cached after the first access.

        Returns
        -------
        np.ndarray
            1D array of cell-center x-coordinates, shape ``(ni,)``.
        """
        if self._x_center is None:
            self._x_center = 0.5 * (self.x_vertex[:-1] + self.x_vertex[1:])
        return self._x_center

    @property
    def y_center(self) -> np.ndarray:
        """Return the 1D array of cell-center y-coordinates.

        Computed as the midpoint between consecutive y-vertices. The result
        is cached after the first access.

        Returns
        -------
        np.ndarray
            1D array of cell-center y-coordinates, shape ``(nj,)``.
        """
        if self._y_center is None:
            self._y_center = 0.5 * (self.y_vertex[:-1] + self.y_vertex[1:])
        return self._y_center

    @property
    def xx_vertex(self) -> np.ndarray:
        """Return the 2D meshgrid of vertex x-coordinates.

        Computed jointly with ``yy_vertex`` on first access and cached.

        Returns
        -------
        np.ndarray
            2D array of vertex x-coordinates, shape ``(nj+1, ni+1)``.
        """
        if self._xx_vertex is None:
            self._xx_vertex, self._yy_vertex = self._build_mesh(self.x_vertex, self.y_vertex)
        return self._xx_vertex

    @property
    def yy_vertex(self) -> np.ndarray:
        """Return the 2D meshgrid of vertex y-coordinates.

        Computed jointly with ``xx_vertex`` on first access and cached.

        Returns
        -------
        np.ndarray
            2D array of vertex y-coordinates, shape ``(nj+1, ni+1)``.
        """
        if self._yy_vertex is None:
            self._xx_vertex, self._yy_vertex = self._build_mesh(self.x_vertex, self.y_vertex)
        return self._yy_vertex

    @property
    def xx_center(self) -> np.ndarray:
        """Return the 2D meshgrid of cell-center x-coordinates.

        Computed jointly with ``yy_center`` on first access and cached.

        Returns
        -------
        np.ndarray
            2D array of cell-center x-coordinates, shape ``(nj, ni)``.
        """
        if self._xx_center is None:
            self._xx_center, self._yy_center = self._build_mesh(self.x_center, self.y_center)
        return self._xx_center

    @property
    def yy_center(self) -> np.ndarray:
        """Return the 2D meshgrid of cell-center y-coordinates.

        Computed jointly with ``xx_center`` on first access and cached.

        Returns
        -------
        np.ndarray
            2D array of cell-center y-coordinates, shape ``(nj, ni)``.
        """
        if self._yy_center is None:
            self._xx_center, self._yy_center = self._build_mesh(self.x_center, self.y_center)
        return self._yy_center

    # ----------------------------
    # Cell center mesh (2D)
    # ----------------------------

    def _build_mesh(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Build a 2D meshgrid with ``indexing='ij'`` row-major ordering.

        Parameters
        ----------
        x : np.ndarray
            1D coordinate array along the i-axis.
        y : np.ndarray
            1D coordinate array along the j-axis.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            ``(xx, yy)`` 2D arrays with shapes ``(len(y), len(x))``.
        """
        yy, xx = np.meshgrid(
            y,
            x,
            indexing="ij"
        )
        return xx, yy
