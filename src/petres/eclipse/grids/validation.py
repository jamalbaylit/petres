from __future__ import annotations

import numpy as np


# ---------------------------------------------------------
# SPECGRID
# ---------------------------------------------------------

def validate_specgrid(dim: np.ndarray) -> tuple[int, int, int]:
    """Validate a SPECGRID dimension array.

    Parameters
    ----------
    dim : np.ndarray
        Array containing at least the first three SPECGRID dimensions.

    Returns
    -------
    tuple[int, int, int]
        The validated ``NI``, ``NJ``, and ``NK`` dimensions.

    Raises
    ------
    ValueError
        If fewer than three values are provided, if any of the first three
        values cannot be converted to integers, or if any dimension is not
        positive.
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
    coord: np.ndarray,
    *,
    ni: int,
    nj: int,
) -> None:
    """Validate the COORD array shape.

    Parameters
    ----------
    coord : np.ndarray
        Coordinate array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array shape does not match ``((nj + 1), (ni + 1), 6)``.
    """

    expected_shape = ((nj + 1), (ni + 1), 6)

    if coord.shape != expected_shape:
        raise ValueError(
            f"COORD shape mismatch: expected "
            f"{expected_shape}, got {coord.shape}"
        )

def validate_coord_array_size(
    coord: np.ndarray,
    *,
    ni: int,
    nj: int,
) -> None:
    """Validate the COORD array size.

    Parameters
    ----------
    coord : np.ndarray
        Coordinate array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array size does not match ``(ni + 1) * (nj + 1) * 6``.
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
    zcorn: np.ndarray,
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate the ZCORN array size.

    Parameters
    ----------
    zcorn : np.ndarray
        Corner-point depth array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.
    nk : int
        Number of cells in the K direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array size does not match ``ni * nj * nk * 8``.
    """
    expected_size = ni * nj * nk * 8

    if zcorn.size != expected_size:
        raise ValueError(
            f"ZCORN size mismatch: expected "
            f"{ni}*{nj}*{nk}*8={expected_size}, got {zcorn.size}"
        )


def validate_zcorn_array_shape(
    zcorn: np.ndarray,
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate the ZCORN array shape.

    Parameters
    ----------
    zcorn : np.ndarray
        Corner-point depth array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.
    nk : int
        Number of cells in the K direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array shape does not match ``(2 * nk, 2 * nj, 2 * ni)``.
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
    actnum: np.ndarray,
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate the ACTNUM array size.

    Parameters
    ----------
    actnum : np.ndarray
        Activity mask array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.
    nk : int
        Number of cells in the K direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array size does not match ``ni * nj * nk``.
    """
    expected_size = ni * nj * nk

    if actnum.size != expected_size:
        raise ValueError(
            f"ACTNUM size mismatch: expected "
            f"{ni}*{nj}*{nk}={expected_size}, got {actnum.size}"
        )

def validate_actnum_array_shape(
    actnum: np.ndarray,
    *,
    ni: int,
    nj: int,
    nk: int,
) -> None:
    """Validate the ACTNUM array shape.

    Parameters
    ----------
    actnum : np.ndarray
        Activity mask array to validate.
    ni : int
        Number of cells in the I direction. Must be non-negative.
    nj : int
        Number of cells in the J direction. Must be non-negative.
    nk : int
        Number of cells in the K direction. Must be non-negative.

    Raises
    ------
    ValueError
        If the array shape does not match ``(nk, nj, ni)``.
    """
    expected_shape = (nk, nj, ni)

    if actnum.shape != expected_shape:
        raise ValueError(
            f"ACTNUM shape mismatch: expected "
            f"{expected_shape}, got {actnum.shape}"
        )

