import numpy as np


# ---------------------------------------------------------
# SPECGRID
# ---------------------------------------------------------

def validate_specgrid(dim: np.ndarray) -> tuple[int, int, int]:
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
) -> np.ndarray:

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
) -> np.ndarray:
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
) -> np.ndarray: 
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
) -> np.ndarray:

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
) -> np.ndarray:
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
) -> np.ndarray:
    expected_shape = (nk, nj, ni)

    if actnum.shape != expected_shape:
        raise ValueError(
            f"ACTNUM shape mismatch: expected "
            f"{expected_shape}, got {actnum.shape}"
        )

