from __future__ import annotations

from io import StringIO
from pathlib import Path

import numpy as np
import pytest

from petres.eclipse.grids.read import GRDECLReader
from petres.eclipse.grids.write import GRDECLWriter
from petres.grids import CornerPointGrid


def test_grdecl_reader_reads_minimal_fixture(minimal_grdecl_path: Path):
    data = GRDECLReader().read(minimal_grdecl_path)

    assert (data.ni, data.nj, data.nk) == (2, 2, 1)
    assert data.coord.shape == (3, 3, 6)
    assert data.zcorn.shape == (2, 4, 4)
    assert data.actnum is not None
    assert data.actnum.shape == (1, 2, 2)


def test_grdecl_reader_clean_comments_removes_inline_content():
    text = "SPECGRID -- inline\n2 2 1 /"
    cleaned = GRDECLReader.clean_comments(text)
    assert "inline" not in cleaned


def test_grdecl_reader_expands_eclipse_repetition():
    arr = GRDECLReader()._get_keyword_array("SPECGRID\n3*2 /", "SPECGRID", dtype=int)
    np.testing.assert_array_equal(arr, np.array([2, 2, 2]))


def test_grdecl_reader_raises_for_missing_terminating_slash(tmp_path: Path):
    bad = tmp_path / "bad.grdecl"
    bad.write_text("SPECGRID\n1 1 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="terminating '/'"):
        GRDECLReader().read(bad)


def test_grdecl_reader_use_actnum_false_returns_none(minimal_grdecl_path: Path):
    data = GRDECLReader().read(minimal_grdecl_path, use_actnum=False)
    assert data.actnum is None


def test_writer_rle_compresses_binary_actnum_tokens():
    f = StringIO()
    actnum = np.array([[[1, 1, 1, 0, 0, 1]]], dtype=bool)
    f = GRDECLWriter._write_array(f, "ACTNUM", actnum, type=np.int8, nan_fill=0, rle=True)
    
    text = f.getvalue()

    assert "3*1" in text
    assert "2*0" in text


def test_cornerpoint_to_grdecl_and_back_roundtrip(simple_cornerpoint_grid, tmp_path: Path):
    path = tmp_path / "roundtrip.grdecl"
    simple_cornerpoint_grid.to_grdecl(path)
    rebuilt = CornerPointGrid.from_grdecl(path)

    assert rebuilt.shape == simple_cornerpoint_grid.shape
    np.testing.assert_allclose(rebuilt.zcorn, simple_cornerpoint_grid.zcorn)
    np.testing.assert_array_equal(rebuilt.active, simple_cornerpoint_grid.active)


def test_reader_rejects_invalid_coord_size(tmp_path: Path):
    bad = tmp_path / "invalid_coord.grdecl"
    bad.write_text(
        """
SPECGRID
2 2 1 1 F /
COORD
53*0.0 /
ZCORN
32*1000.0 /
ACTNUM
4*1 /
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="COORD size mismatch"):
        GRDECLReader().read(bad)
