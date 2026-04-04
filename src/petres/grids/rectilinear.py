from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from numpy.typing import ArrayLike, NDArray


@dataclass
class Rectilinear2DGrid:
    """Represent a 2D structured rectilinear grid.

    The class stores vertex coordinates in each axis and computes cell-center
    coordinates and coordinate meshes on demand.

    Parameters
    ----------
    x_vertex : ArrayLike
        1D vertex coordinates along x of length ``ni+1``.
    y_vertex : ArrayLike
        1D vertex coordinates along y of length ``nj+1``.
    active : ArrayLike
        Boolean mask of shape ``(nj, ni)`` indicating active cells.

    Raises
    ------
    ValueError
        If ``active`` does not match the expected shape ``(nj, ni)``.

    Notes
    -----
    Coordinate meshes are cached lazily and reused after first computation.
    """

    x_vertex: NDArray[np.float64]   # Grid line coordinates (ni+1,)
    y_vertex: NDArray[np.float64]   # Grid line coordinates (nj+1,)
    active: NDArray[np.bool_]     # Boolean mask (nj, ni)
    
    # --- cached 1D centers ---
    _x_center: NDArray[np.float64] | None = field(init=False, repr=False, default=None)
    _y_center: NDArray[np.float64] | None = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_vertex: NDArray[np.float64] | None = field(init=False, repr=False, default=None)
    _yy_vertex: NDArray[np.float64] | None = field(init=False, repr=False, default=None)

    # --- cached 2D center mesh ---
    _xx_center: NDArray[np.float64] | None = field(init=False, repr=False, default=None)
    _yy_center: NDArray[np.float64] | None = field(init=False, repr=False, default=None)

    def __init__(self, x_vertex: ArrayLike, y_vertex: ArrayLike, active: ArrayLike) -> None:
        """Initialize the rectilinear grid and validate input shapes.

        Raises
        ------
        ValueError
            If ``active`` does not match the expected shape ``(nj, ni)``.
        """
        self.x_vertex = np.asarray(x_vertex)
        self.y_vertex = np.asarray(y_vertex)
        self.active = np.asarray(active, dtype=bool)

        self._x_center = None
        self._y_center = None
        self._xx_vertex = None
        self._yy_vertex = None
        self._xx_center = None
        self._yy_center = None

        self.__post_init__()

    def __post_init__(self) -> None:
        """Validate normalized arrays and enforce the activity-mask shape.

        Raises
        ------
        ValueError
            If ``active`` does not match the expected cell shape ``(nj, ni)``.

        Notes
        -----
        This method assumes arrays were already converted to NumPy arrays by
        :meth:`__init__`.
        """
        self.x_vertex = np.asarray(self.x_vertex)
        self.y_vertex = np.asarray(self.y_vertex)
        self.active = np.asarray(self.active, dtype=bool)

        expected_shape = (self.nj, self.ni)
        if self.active.shape != expected_shape:
            raise ValueError(
                f"'active' shape must be {expected_shape}, got {self.active.shape}."
            )

    @property
    def cell_shape(self) -> tuple[int, int]:
        """Get the number of cells along j and i.

        Returns
        -------
        tuple of int
            Cell grid shape as ``(nj, ni)``.
        """
        return (self.nj, self.ni)

    @property
    def vertex_shape(self) -> tuple[int, int]:
        """Get the number of vertices along j and i.

        Returns
        -------
        tuple of int
            Vertex grid shape as ``(nj + 1, ni + 1)``.
        """
        return (self.njv, self.niv)

    # ----------------------------
    # Derived sizes
    # ----------------------------

    @property
    def niv(self) -> int:
        """Get the number of vertices in the i-direction.

        Returns
        -------
        int
            Number of x-direction vertices, equivalent to ``ni + 1``.
        """
        return self.x_vertex.size


    @property
    def njv(self) -> int:
        """Get the number of vertices in the j-direction.

        Returns
        -------
        int
            Number of y-direction vertices, equivalent to ``nj + 1``.
        """
        return self.y_vertex.size


    @property
    def ni(self) -> int:
        """Get the number of cells in the i-direction.

        Returns
        -------
        int
            Number of i-direction cells.
        """
        return self.niv - 1


    @property
    def nj(self) -> int:
        """Get the number of cells in the j-direction.

        Returns
        -------
        int
            Number of j-direction cells.
        """
        return self.njv - 1


    # ----------------------------
    # Cell centers (1D)
    # ----------------------------
    @property
    def x_center(self) -> NDArray[np.float64]:
        """Get 1D x cell-center coordinates.

        Returns
        -------
        numpy.ndarray
            Array of length ``ni`` containing x center coordinates.
        """
        if self._x_center is None:
            self._x_center = 0.5 * (self.x_vertex[:-1] + self.x_vertex[1:])
        return self._x_center

    @property
    def y_center(self) -> NDArray[np.float64]:
        """Get 1D y cell-center coordinates.

        Returns
        -------
        numpy.ndarray
            Array of length ``nj`` containing y center coordinates.
        """
        if self._y_center is None:
            self._y_center = 0.5 * (self.y_vertex[:-1] + self.y_vertex[1:])
        return self._y_center

    @property
    def xx_vertex(self) -> NDArray[np.float64]:
        """Get x coordinates on the 2D vertex mesh.

        Returns
        -------
        numpy.ndarray
            2D array with shape ``(nj + 1, ni + 1)``.
        """
        if self._xx_vertex is None:
            self._xx_vertex, self._yy_vertex = self._build_mesh(self.x_vertex, self.y_vertex)
        return self._xx_vertex
    
    @property
    def yy_vertex(self) -> NDArray[np.float64]:
        """Get y coordinates on the 2D vertex mesh.

        Returns
        -------
        numpy.ndarray
            2D array with shape ``(nj + 1, ni + 1)``.
        """
        if self._yy_vertex is None:
            self._xx_vertex, self._yy_vertex = self._build_mesh(self.x_vertex, self.y_vertex)
        return self._yy_vertex
    
    @property
    def xx_center(self) -> NDArray[np.float64]:
        """Get x coordinates on the 2D cell-center mesh.

        Returns
        -------
        numpy.ndarray
            2D array with shape ``(nj, ni)``.
        """
        if self._xx_center is None:
            self._xx_center, self._yy_center = self._build_mesh(self.x_center, self.y_center)
        return self._xx_center
    
    @property
    def yy_center(self) -> NDArray[np.float64]:
        """Get y coordinates on the 2D cell-center mesh.

        Returns
        -------
        numpy.ndarray
            2D array with shape ``(nj, ni)``.
        """
        if self._yy_center is None:
            self._xx_center, self._yy_center = self._build_mesh(self.x_center, self.y_center)
        return self._yy_center


    # ----------------------------
    # Cell center mesh (2D)
    # ----------------------------
    def _build_mesh(self, x: NDArray[np.float64], y: NDArray[np.float64]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        """Build 2D coordinate meshes from 1D arrays.

        Parameters
        ----------
        x : numpy.ndarray
            1D i-direction coordinates.
        y : numpy.ndarray
            1D j-direction coordinates.

        Returns
        -------
        tuple of numpy.ndarray
            ``(xx, yy)`` coordinate meshes with ``ij`` indexing.
        """
        yy, xx = np.meshgrid(
            y,
            x,
            indexing="ij"
        )
        return xx, yy
