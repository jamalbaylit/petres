from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import numpy as np
from numpy.typing import DTypeLike, NDArray

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
    """Container for parsed GRDECL grid arrays and dimensions.

    Parameters
    ----------
    ni : int
        Number of cells in the I direction.
    nj : int
        Number of cells in the J direction.
    nk : int
        Number of cells in the K direction.
    coord : numpy.ndarray
        COORD array reshaped to ``(nj + 1, ni + 1, 6)``.
    zcorn : numpy.ndarray
        ZCORN array reshaped to ``(2 * nk, 2 * nj, 2 * ni)``.
    actnum : numpy.ndarray of int or None
        ACTNUM array reshaped to ``(nk, nj, ni)``, or ``None`` if missing or
        disabled.
    """

    ni: int
    nj: int
    nk: int
    coord: NDArray[np.float64]   # (nj+1, ni+1, 6)
    zcorn: NDArray[np.float64]   # (2*nk, 2*nj, 2*ni)
    actnum: NDArray[np.int_] | None  # (nk, nj, ni) or None


class GRDECLReader:
    """Read Eclipse GRDECL grid keywords into validated NumPy arrays.

    Parameters
    ----------
    take_last : bool, default=True
        Whether to use the last occurrence of a keyword when the same
        keyword appears multiple times in a deck.

    Notes
    -----
    The reader extracts and validates the ``SPECGRID``, ``COORD``, and
    ``ZCORN`` keywords and optionally parses ``ACTNUM``.

    Eclipse decks may redefine keywords later in the file. Setting
    ``take_last=True`` matches that overriding behavior.
    """

    def __init__(self, *, take_last: bool = True):
        """Initialize the GRDECL reader."""
        # In decks, later keywords can override earlier ones.
        self.take_last = take_last

    @staticmethod
    def clean_comments(text: str) -> str:
        """Remove inline Eclipse comments from text.

        Parameters
        ----------
        text : str
            Raw deck text.

        Returns
        -------
        str
            Text with portions after ``--`` removed on each line.
        """
        # Remove inline comments starting with --
        out = []
        for line in text.splitlines():
            if "--" in line:
                line = line.split("--", 1)[0]
            out.append(line)
        return "\n".join(out)

    def read(self, path: str | Path, *, use_actnum: bool = True) -> GRDECLData:
        """Read and validate grid keywords from a GRDECL file.

        Parameters
        ----------
        path : str or pathlib.Path
            Path to the GRDECL file.
        use_actnum : bool, default=True
            Whether to parse and validate ``ACTNUM`` when it exists.

        Returns
        -------
        GRDECLData
            Parsed dimensions and reshaped keyword arrays.

        Raises
        ------
        ValueError
            If required keywords are missing or keyword data are malformed.
        """
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
        """Locate text immediately after a keyword line.

        Parameters
        ----------
        text : str
        keyword : str

        Returns
        -------
        str or None
        """
        pattern = rf"^[ \t]*{re.escape(keyword)}\b.*$"
        matches = list(re.finditer(pattern, text, flags=re.MULTILINE))
        if not matches:
            return None
        m = matches[-1] if self.take_last else matches[0]
        return text[m.end():]  # text after the keyword line

    @staticmethod
    def _extract_until_slash(text_after_keyword: str) -> str:
        """Extract keyword payload up to the terminating slash.

        Parameters
        ----------
        text_after_keyword : str

        Returns
        -------
        str

        Raises
        ------
        ValueError
            If no terminating slash is present.
        """
        idx = text_after_keyword.find("/")
        if idx == -1:
            raise ValueError("Keyword block does not contain terminating '/'.")
        return text_after_keyword[:idx]

    @staticmethod
    def _expand_ecl_pattern(s: str) -> str:
        """Expand Eclipse repeat syntax into explicit tokens.

        Parameters
        ----------
        s : str

        Returns
        -------
        str
        """
        # Expand Eclipse repetition like: 10*0.25
        pattern = re.compile(r"(\d+)\*([^\s]+)")
        def repl(m: re.Match[str]) -> str:
            n = int(m.group(1))
            val = m.group(2)
            return " ".join([val] * n)
        return pattern.sub(repl, s)

    def _get_keyword_content(self, text: str, keyword: str) -> str:
        """Get normalized raw content for a keyword block.

        Parameters
        ----------
        text : str
        keyword : str

        Returns
        -------
        str

        Raises
        ------
        ValueError
            If the keyword is missing or has no valid terminator.
        """
        cropped = self._find_keyword_block_start(text, keyword)
        if cropped is None:
            raise ValueError(f"{keyword} not found in GRDECL file.")
        raw = self._extract_until_slash(cropped)
        raw = re.sub(r"\s+", " ", raw).strip()
        return raw

    def _get_keyword_array(
        self,
        text: str,
        keyword: str,
        dtype: DTypeLike = float,
    ) -> NDArray[Any]:
        """Parse a keyword block into a NumPy array.

        Parameters
        ----------
        text : str
        keyword : str
        dtype : numpy.typing.DTypeLike, default=float

        Returns
        -------
        numpy.ndarray
        """
        content = self._get_keyword_content(text, keyword)
        content = self._expand_ecl_pattern(content)
        if not content:
            return np.array([], dtype=dtype)
        return np.array(content.split(), dtype=dtype)

    def _has_keyword(self, text: str, keyword: str) -> bool:
        """Check whether a keyword exists as a standalone deck token.

        Parameters
        ----------
        text : str
        keyword : str

        Returns
        -------
        bool
        """
        # Fast-ish presence check with boundary
        return re.search(rf"^[ \t]*{re.escape(keyword)}\b", text, flags=re.MULTILINE) is not None