from __future__ import annotations

"""Eclipse corner-point grid I/O and keyword utilities.

This package exposes readers, writers, and reference data for Eclipse
GRDECL corner-point grids.

Public API
----------
GRDECLData
    Immutable container for parsed GRDECL dimensions and arrays.
GRDECLReader
    Parser that reads GRDECL files into validated NumPy arrays.
GRDECLWriter
    Writer that serialises corner-point grids to GRDECL files.
CELL_KEYWORDS
    Mapping of well-known Eclipse cell-property keywords to descriptions.
"""

from .keywords import CELL_KEYWORDS
from .read import GRDECLData, GRDECLReader
from .write import GRDECLWriter

__all__: list[str] = [
    "CELL_KEYWORDS",
    "GRDECLData",
    "GRDECLReader",
    "GRDECLWriter",
]
