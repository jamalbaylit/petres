from __future__ import annotations

import numpy as np
import pytest

from petres.eclipse.grids.validation import (
    validate_actnum_array_shape,
    validate_coord_array_shape,
    validate_specgrid,
    validate_zcorn_array_size,
)


def test_validate_specgrid_rejects_non_positive_dims():
    with pytest.raises(ValueError, match="Invalid SPECGRID dimensions"):
        validate_specgrid(np.array([2, 0, 1]))


def test_validate_coord_array_shape_rejects_mismatch():
    coord = np.zeros((2, 2, 6), dtype=float)
    with pytest.raises(ValueError, match="COORD shape mismatch"):
        validate_coord_array_shape(coord, ni=2, nj=2)


def test_validate_zcorn_array_size_rejects_wrong_total_size():
    zcorn = np.zeros(15, dtype=float)
    with pytest.raises(ValueError, match="ZCORN size mismatch"):
        validate_zcorn_array_size(zcorn, ni=1, nj=1, nk=2)


def test_validate_actnum_array_shape_rejects_incorrect_ordering():
    actnum = np.ones((2, 1, 1), dtype=int)
    with pytest.raises(ValueError, match="ACTNUM shape mismatch"):
        validate_actnum_array_shape(actnum, ni=2, nj=1, nk=1)
