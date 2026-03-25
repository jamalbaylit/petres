from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import re

from .validation import (
    validate_specgrid, 
    validate_coord_array_shape, 
    validate_coord_array_size, 
    validate_zcorn_array_shape, 
    validate_zcorn_array_size,
    validate_actnum_array_shape,
    validate_actnum_array_size,
)

@dataclass(frozen=True)
class GRDECLData:
    ni: int
    nj: int
    nk: int
    coord: np.ndarray   # (nj+1, ni+1, 6)
    zcorn: np.ndarray   # (2*nk, 2*nj, 2*ni)
    actnum: np.ndarray | None  # (nk, nj, ni) or None


class GRDECLReader:
    """
    Reads GRDECL (ECLIPSE) grid keywords:
    - SPECGRID (NI, NJ, NK)
    - COORD
    - ZCORN
    - ACTNUM (optional)
    """

    def __init__(self, *, take_last: bool = True):
        # In decks, later keywords can override earlier ones.
        self.take_last = take_last

    @staticmethod
    def clean_comments(text: str) -> str:
        # Remove inline comments starting with --
        out = []
        for line in text.splitlines():
            if "--" in line:
                line = line.split("--", 1)[0]
            out.append(line)
        return "\n".join(out)

    def read(self, path: str | Path, *, use_actnum: bool = True) -> GRDECLData:
        path = Path(path)
        text = path.read_text(encoding="utf-8", errors="ignore")
        text = self.clean_comments(text)

        dim = self._get_keyword_array(text, "SPECGRID", dtype=str)
        dim = validate_specgrid(dim)
        ni, nj, nk = dim

        coord = self._get_keyword_array(text, "COORD", dtype=float)
        validate_coord_array_size(coord, ni=ni, nj=nj)
        coord = coord.reshape((nj + 1, ni + 1, 6))
        validate_coord_array_shape(coord, ni=ni, nj=nj)

        zcorn = self._get_keyword_array(text, "ZCORN", dtype=float)
        validate_zcorn_array_size(zcorn, ni=ni, nj=nj, nk=nk)
        zcorn = zcorn.reshape((2 * nk, 2 * nj, 2 * ni))
        validate_zcorn_array_shape(zcorn, ni=ni, nj=nj, nk=nk)

        actnum = None
        if self._has_keyword(text, "ACTNUM") and use_actnum:
            act = self._get_keyword_array(text, "ACTNUM", dtype=int)
            validate_actnum_array_size(act, ni=ni, nj=nj, nk=nk)
            actnum = act.reshape((nk, nj, ni))
            validate_actnum_array_shape(actnum, ni=ni, nj=nj, nk=nk)

        return GRDECLData(ni=ni, nj=nj, nk=nk, coord=coord, zcorn=zcorn, actnum=actnum)

    # ----------------------------
    # helpers
    # ----------------------------

    def _find_keyword_block_start(self, text: str, keyword: str) -> str | None:
        pattern = rf"^[ \t]*{re.escape(keyword)}\b.*$"
        matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
        if not matches:
            return None
        m = matches[-1] if self.take_last else matches[0]
        return text[m.end():]  # text after the keyword line

    @staticmethod
    def _extract_until_slash(text_after_keyword: str) -> str:
        idx = text_after_keyword.find("/")
        if idx == -1:
            raise ValueError("Keyword block does not contain terminating '/'.")
        return text_after_keyword[:idx]

    @staticmethod
    def _expand_ecl_pattern(s: str) -> str:
        # Expand Eclipse repetition like: 10*0.25
        pattern = re.compile(r"(\d+)\*([^\s]+)")
        def repl(m):
            n = int(m.group(1))
            val = m.group(2)
            return " ".join([val] * n)
        return pattern.sub(repl, s)

    def _get_keyword_content(self, text: str, keyword: str) -> str:
        cropped = self._find_keyword_block_start(text, keyword)
        if cropped is None:
            raise ValueError(f"{keyword} not found in GRDECL file.")
        raw = self._extract_until_slash(cropped)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw

    def _get_keyword_array(self, text: str, keyword: str, dtype=float) -> np.ndarray:
        content = self._get_keyword_content(text, keyword)
        content = self._expand_ecl_pattern(content)
        if not content:
            return np.array([], dtype=dtype)
        return np.array(content.split(), dtype=dtype)

    def _has_keyword(self, text: str, keyword: str) -> bool:
        # Fast-ish presence check with boundary
        return re.search(rf"^[ \t]*{re.escape(keyword)}\b", text, flags=re.MULTILINE) is not None