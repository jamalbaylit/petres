from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass
class Rectilinear2DGrid:
    """2D structured rectilinear grid with lazy-evaluated cell centers.

    Parameters
    ----------
    x_vertex : np.ndarray
        1D array of grid line coordinates along x, of size ``ni + 1``.
    y_vertex : np.ndarray
        1D array of grid line coordinates along y, of size ``nj + 1``.
    active : np.ndarray
        Boolean mask of active cells with shape ``(nj, ni)``.

    Notes
    -----
    Cell-center coordinates (``x_center``, ``y_center``) and 2D meshgrids
    (``xx_vertex``, ``yy_vertex``, ``xx_center``, ``yy_center``) are computed
    lazily and cached on first access.
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
        """
        return self.x_vertex.size


    @property
    def njv(self) -> int:
        """Return the number of vertices in the j-direction.

        This corresponds to the length of the y-vertex coordinate array.
        For a structured grid with nj cells in the j-direction,
        the number of vertices is njv = nj + 1.
        """
        return self.y_vertex.size


    @property
    def ni(self) -> int:
        """Return the number of cells in the i-direction.

        Cells are defined between consecutive vertices.
        Therefore, ni = niv - 1.
        """
        return self.niv - 1


    @property
    def nj(self) -> int:
        """Return the number of cells in the j-direction.

        Cells are defined between consecutive vertices.
        Therefore, nj = njv - 1.
        """
        return self.njv - 1


    # ----------------------------
    # Cell centers (1D)
    # ----------------------------
    @property
    def x_center(self) -> np.ndarray:
        """Return the 1D array of cell-center coordinates along x.

        Returns
        -------
        np.ndarray
            Cell-center x-coordinates of shape ``(ni,)``.
        """
        if self._x_center is None:
            self._x_center = 0.5 * (self.x_vertex[:-1] + self.x_vertex[1:])
        return self._x_center

    @property
    def y_center(self) -> np.ndarray:
        """Return the 1D array of cell-center coordinates along y.

        Returns
        -------
        np.ndarray
            Cell-center y-coordinates of shape ``(nj,)``.
        """
        if self._y_center is None:
            self._y_center = 0.5 * (self.y_vertex[:-1] + self.y_vertex[1:])
        return self._y_center

    @property
    def xx_vertex(self) -> np.ndarray:
        """Return the 2D meshgrid of vertex x-coordinates.

        Returns
        -------
        np.ndarray
            X-coordinates at all vertices with shape ``(nj+1, ni+1)``.
        """
        if self._xx_vertex is None:
            self._xx_vertex, self._yy_vertex =  self._build_mesh(self.x_vertex, self.y_vertex)
        return self._xx_vertex

    @property
    def yy_vertex(self) -> np.ndarray:
        """Return the 2D meshgrid of vertex y-coordinates.

        Returns
        -------
        np.ndarray
            Y-coordinates at all vertices with shape ``(nj+1, ni+1)``.
        """
        if self._yy_vertex is None:
            self._xx_vertex, self._yy_vertex =  self._build_mesh(self.x_vertex, self.y_vertex)
        return self._yy_vertex

    @property
    def xx_center(self) -> np.ndarray:
        """Return the 2D meshgrid of cell-center x-coordinates.

        Returns
        -------
        np.ndarray
            X-coordinates at all cell centers with shape ``(nj, ni)``.
        """
        if self._xx_center is None:
            self._xx_center, self._yy_center =  self._build_mesh(self.x_center, self.y_center)
        return self._xx_center

    @property
    def yy_center(self) -> np.ndarray:
        """Return the 2D meshgrid of cell-center y-coordinates.

        Returns
        -------
        np.ndarray
            Y-coordinates at all cell centers with shape ``(nj, ni)``.
        """
        if self._yy_center is None:
            self._xx_center, self._yy_center =  self._build_mesh(self.x_center, self.y_center)
        return self._yy_center


    # ----------------------------
    # Cell center mesh (2D)
    # ----------------------------
    def _build_mesh(self, x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Build a 2D meshgrid from 1D coordinate arrays using ``ij`` indexing.

        Parameters
        ----------
        x : np.ndarray
            1D array of x-coordinates.
        y : np.ndarray
            1D array of y-coordinates.

        Returns
        -------
        tuple[np.ndarray, np.ndarray]
            ``(xx, yy)`` meshgrid arrays, each of shape ``(len(y), len(x))``.
        """
        yy, xx = np.meshgrid(
            y,
            x,
            indexing="ij"
        )
        return xx, yy
