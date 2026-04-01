from __future__ import annotations

"""Eclipse GRDECL corner-point grid I/O.

Provides a reader, writer, and immutable data container for the Eclipse
GRDECL grid format together with supporting keyword constants.

Classes
-------
GRDECLData
    Immutable container for parsed GRDECL dimensions and arrays.
GRDECLReader
    Parser that reads and validates GRDECL keyword blocks into NumPy arrays.
GRDECLWriter
    Writer that serialises corner-point grids and property arrays to GRDECL
    files.

Constants
---------
CELL_KEYWORDS : dict[str, str]
    Mapping of recognised per-cell Eclipse keyword names to short descriptions.
"""

from .keywords import CELL_KEYWORDS
from .read import GRDECLData, GRDECLReader
from .write import GRDECLWriter

__all__ = [
    "CELL_KEYWORDS",
    "GRDECLData",
    "GRDECLReader",
    "GRDECLWriter",
]
