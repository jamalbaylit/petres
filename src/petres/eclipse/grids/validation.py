from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------
# SPECGRID
# ---------------------------------------------------------

def validate_specgrid(dim: NDArray[np.str_]) -> tuple[int, int, int]:
    """Validate SPECGRID dimension tokens and return parsed grid extents.

    Parameters
    ----------
    dim : NDArray[np.str_]
        Raw token array extracted from the SPECGRID keyword block.
        Must contain at least three elements representing NI, NJ, NK.

    Returns
    -------
    tuple of int
        A three-element tuple ``(ni, nj, nk)`` with each dimension
        guaranteed to be a strictly positive integer.

    Raises
    ------
    ValueError
        If ``dim`` contains fewer than 3 elements, if the first three
        tokens cannot be cast to integers, or if any dimension is
        non-positive.
    """
    if dim.size < 3:
        raise ValueError(
            f"SPECGRID must have at least 3 values (NI NJ NK). "
            f"Got: {dim[:10]}"
        )
    # Check integer values
    try:
        ni, nj, nk = int(dim[0]), int(dim[1]), int(dim[2])
    except ValueError:
        raise ValueError(
            f"SPECGRID first 4 values must be integers. Got: {dim[:4]}"
        )
    
    if ni <= 0 or nj <= 0 or nk <= 0:
        raise ValueError(
            f"Invalid SPECGRID dimensions: NI={ni}, NJ={nj}, NK={nk}"
        )

    return ni, nj, nk


# ---------------------------------------------------------
# COORD
# ---------------------------------------------------------

def validate_coord_array_shape(
    coord: NDArray[np.float64],
    *,
    ni: int,
    nj: int,
) -> None:
    """Validate that a reshaped COORD array has the expected shape.

    Parameters
    ----------
    coord : NDArray[np.float64]
        COORD array to validate. Expected shape is
        ``(nj + 1, ni + 1, 6)``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.

    Raises
    ------
    ValueError
        If ``coord.shape`` does not equal ``(nj + 1, ni + 1, 6)``.
    """
    expected_shape = ((nj + 1), (ni + 1), 6)

    if coord.shape != expected_shape:
        raise ValueError(
            f"COORD shape mismatch: expected "
            f"{expected_shape}, got {coord.shape}"
        )
    
def validate_coord_array_size(
    coord: NDArray[np.float64],
    *,
    ni: int,
    nj: int,
) -> None:
    """Validate that a flat COORD array contains the expected number of values.

    Parameters
    ----------
    coord : NDArray[np.float64]
        Flat COORD array to validate. Expected size is
        ``(ni + 1) * (nj + 1) * 6``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.

    Raises
    ------
    ValueError
        If ``coord.size`` does not equal ``(ni + 1) * (nj + 1) * 6``.
    """
    expected_size = (ni + 1) * (nj + 1) * 6

    if coord.size != expected_size:
        raise ValueError(
            f"COORD size mismatch: expected "
            f"{(ni+1)}*{(nj+1)}*6={expected_size}, got {coord.size}"
        )

# ---------------------------------------------------------
# ZCORN
# ---------------------------------------------------------
def validate_zcorn_array_size(
    zcorn: NDArray[np.float64],
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate that a flat ZCORN array contains the expected number of values.

    Parameters
    ----------
    zcorn : NDArray[np.float64]
        Flat ZCORN array to validate. Expected size is
        ``ni * nj * nk * 8``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.
    nk : int
        Number of cells in the K direction.

    Raises
    ------
    ValueError
        If ``zcorn.size`` does not equal ``ni * nj * nk * 8``.
    """
    expected_size = ni * nj * nk * 8

    if zcorn.size != expected_size:
        raise ValueError(
            f"ZCORN size mismatch: expected "
            f"{ni}*{nj}*{nk}*8={expected_size}, got {zcorn.size}"
        )


def validate_zcorn_array_shape(
    zcorn: NDArray[np.float64],
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate that a reshaped ZCORN array has the expected shape.

    Parameters
    ----------
    zcorn : NDArray[np.float64]
        ZCORN array to validate. Expected shape is
        ``(2 * nk, 2 * nj, 2 * ni)``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.
    nk : int
        Number of cells in the K direction.

    Raises
    ------
    ValueError
        If ``zcorn.shape`` does not equal ``(2 * nk, 2 * nj, 2 * ni)``.
    """
    expected_shape = (2 * nk, 2 * nj, 2 * ni)

    if zcorn.shape != expected_shape:
        raise ValueError(
            f"ZCORN shape mismatch: expected "
            f"{expected_shape}, got {zcorn.shape}"
        )

# ---------------------------------------------------------
# ACTNUM
# ---------------------------------------------------------
def validate_actnum_array_size(
    actnum: NDArray[np.int_],
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate that a flat ACTNUM array contains the expected number of values.

    Parameters
    ----------
    actnum : numpy.ndarray of int
        Flat ACTNUM array to validate. Expected size is
        ``ni * nj * nk``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.
    nk : int
        Number of cells in the K direction.

    Raises
    ------
    ValueError
        If ``actnum.size`` does not equal ``ni * nj * nk``.
    """
    expected_size = ni * nj * nk

    if actnum.size != expected_size:
        raise ValueError(
            f"ACTNUM size mismatch: expected "
            f"{ni}*{nj}*{nk}={expected_size}, got {actnum.size}"
        )

def validate_actnum_array_shape(
    actnum: NDArray[np.int_],
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate that a reshaped ACTNUM array has the expected shape.

    Parameters
    ----------
    actnum : numpy.ndarray of int
        ACTNUM array to validate. Expected shape is ``(nk, nj, ni)``.
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.
    nk : int
        Number of cells in the K direction.

    Raises
    ------
    ValueError
        If ``actnum.shape`` does not equal ``(nk, nj, ni)``.
    """
    expected_shape = (nk, nj, ni)

    if actnum.shape != expected_shape:
        raise ValueError(
            f"ACTNUM shape mismatch: expected "
            f"{expected_shape}, got {actnum.shape}"
        )

