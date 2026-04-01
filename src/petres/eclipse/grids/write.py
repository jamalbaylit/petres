from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import TextIO

import numpy as np

from ...errors.eclipse import GRDECLMissingValueError

from .validation import (
    validate_specgrid, 
    validate_coord_array_shape, 
    validate_coord_array_size, 
    validate_zcorn_array_shape, 
    validate_zcorn_array_size,
    validate_actnum_array_shape,
    validate_actnum_array_size,
)


class GRDECLWriter:
    """
    Write Eclipse/Petrel corner-point data to GRDECL files.

    The class provides methods for exporting full grids and individual
    properties, including optional run-length encoding for compact output.

    Notes
    -----
    The writer is stateless. Grid arrays are supplied to method calls
    rather than stored on the instance.
    """

    def __init__(self) -> None:
        """Initialize a stateless GRDECL writer."""

    def write_property(
        self,
        path: str | Path,
        *,
        values: np.ndarray,
        keyword: str
    ) -> None:
        """
        Write a single property array as a GRDECL keyword block.

        Parameters
        ----------
        path : str | pathlib.Path
            Destination GRDECL file path.
        values : numpy.ndarray
            Property values to write.
        keyword : str
            Eclipse keyword to associate with ``values`` (for example,
            ``"PORO"`` or ``"PERMX"``).
        """
        with open(path, "w") as f:
            GRDECLWriter._write_array(f, keyword, values, rle=True)

    def write(
        self,
        *,
        path: str | Path,
        coord: np.ndarray, 
        zcorn: np.ndarray, 
        actnum: np.ndarray | None = None,
        property_values: Mapping[str, np.ndarray] | None = None,
        property_keywords: Sequence[str] | None = None,
        rle: bool = True,
        units: str = "FEET",
        mapunits: str = "FEET",
    ) -> None:
        """
        Write a complete corner-point grid to a GRDECL file.

        Parameters
        ----------
        path : str | pathlib.Path
            Destination GRDECL file path.
        coord : numpy.ndarray
            Pillar coordinate array for the ``COORD`` keyword.
        zcorn : numpy.ndarray
            Corner depth array for the ``ZCORN`` keyword with shape
            ``(2 * nk, 2 * nj, 2 * ni)``.
        actnum : numpy.ndarray | None, default=None
            Optional active-cell mask for the ``ACTNUM`` keyword.
        property_values : Mapping[str, numpy.ndarray] | None, default=None
            Optional mapping of property keyword to property array.
        property_keywords : Sequence[str] | None, default=None
            Optional ordered subset of keys from ``property_values``.
            When omitted, all keys from ``property_values`` are written.
        rle : bool, default=True
            If ``True``, use run-length encoding for array export.
        units : str, default="FEET"
            Reserved unit label for grid coordinates.
        mapunits : str, default="FEET"
            Reserved map unit label.

        Raises
        ------
        KeyError
            If ``property_keywords`` contains a keyword not present in
            ``property_values``.
        """
        
        # zcorn is shaped (2*nk, 2*nj, 2*ni); convert back to cell counts
        ni, nj, nk = zcorn.shape[2] // 2, zcorn.shape[1] // 2, zcorn.shape[0] // 2

        with open(path, 'w') as f:
            # Header
            f = self._write_header(f, ni, nj, nk)
            
            # Map units
            # f.write(f"MAPUNITS\n'{mapunits}' /\n")
            
            # # Map axes
            # if mapaxes is not None:
            #     # mapaxes = self._auto_mapaxes()
            #     f.write(f"MAPAXES\n")
            #     f.write(f"{mapaxes[0]:.6f} {mapaxes[1]:.6f}\n")
            #     f.write(f"{mapaxes[2]:.6f} {mapaxes[3]:.6f}\n")
            #     f.write(f"{mapaxes[4]:.6f} {mapaxes[5]:.6f} /\n")
            
            # Grid units
            # f.write(f"GRIDUNIT\n'{units}' /\n")
            
            # SPECGRID
            f.write("\nSPECGRID\n")
            f.write(f"{ni} {nj} {nk}  1  F /\n")
            
            # COORD
            f = GRDECLWriter._write_array(f, "COORD", coord, rle=rle)
            
            # ZCORN
            f = GRDECLWriter._write_array(f, "ZCORN", zcorn, rle=rle)
            
            # ACTNUM
            if actnum is not None:
                f = GRDECLWriter._write_array(f, "ACTNUM", actnum, type=np.int8, nan_fill=0, rle=rle)
            
            # Properties
            if property_values:
                keywords = property_keywords if property_keywords is not None else property_values.keys()
                for prop_name in keywords:
                    if prop_name not in property_values:
                        raise KeyError(f"Property keyword '{prop_name}' is missing from property_values.")
                    prop_array = property_values[prop_name]
                    f = GRDECLWriter._write_array(f, prop_name, prop_array, rle=rle)


    def _write_header(
        self, 
        f: TextIO,
        ni: int,
        nj: int,
        nk: int
    ) -> TextIO:
        """
        Write a metadata header block.

        Parameters
        ----------
        f : TextIO
            Writable text stream.
        ni, nj, nk : int
            Grid cell counts in the I, J, and K directions.

        Returns
        -------
        TextIO
        """
        now = datetime.now()
        date_str = now.strftime("%A, %B %d %Y %H:%M:%S")
        f.write(f"-- Format      : Generic Eclipse style (ASCII) grid geometry and properties (*.GRDECL)\n")
        f.write(f"-- Exported by : Petres\n")
        f.write(f"-- Date        : {date_str}\n")
        f.write(f"-- Grid        : 3D Grid ({ni}X{nj}X{nk})\n")
        f.write("\n"*2)
        return f

    def _auto_mapaxes(self) -> list[float]:
        """
        Compute default MAPAXES coordinates from ``self.COORD``.

        Returns
        -------
        list[float]
            Six-value list representing MAPAXES origin and axis points.
        """
        x_coords = self.COORD[:, :, 0, 0]
        y_coords = self.COORD[:, :, 0, 1]
        
        x_min, x_max = x_coords.min(), x_coords.max()
        y_min, y_max = y_coords.min(), y_coords.max()
        
        # Origin, point on X-axis, point on Y-axis
        return [
            x_min, y_min,  # Origin
            x_min, y_min,  # Point 1 (same as origin)
            x_max, y_min   # Point 2 (along X-axis)
        ]
    
    @staticmethod
    def _write_array(
        f: TextIO, 
        keyword: str,
        array: np.ndarray, 
        ncol: int = 20, 
        type: np.dtype = np.float32, 
        decimals: int | None = None,
        nan_fill: float | int | None = None,
        rle: bool = False
    ) -> TextIO:
        """
        Write an array as a GRDECL keyword block.

        Parameters
        ----------
        f : TextIO
            Writable text stream.
        keyword : str
            GRDECL keyword name.
        array : np.ndarray
            Array values to write.
        ncol : int, default=20
            Values or tokens per output line.
        type : np.dtype, default=np.float32
            Target dtype applied before writing.
        decimals : int | None, default=None
            Decimal places for float formatting; ``None`` uses compact form.
        nan_fill : float | int | None, default=None
            Replacement for NaN entries; ``None`` raises on NaN.
        rle : bool, default=False
            Use run-length encoding when ``True``.

        Returns
        -------
        TextIO
        """  
        
        if np.isinf(array).any():
            raise ValueError(f" Array '{keyword}' contains infinite values.")

        if nan_fill is not None:
            array = np.nan_to_num(array, nan=nan_fill, copy=False)
        else:
            if np.isnan(array).any():
                raise GRDECLMissingValueError(keyword=keyword)
        if rle:
            return GRDECLWriter._write_array_rle(f, keyword, array, ncol, type, decimals)
        else:
            return GRDECLWriter._write_array_raw(f, keyword, array, ncol, type, decimals)

    @staticmethod
    def _normalize_keyword(keyword: str) -> str:
        """
        Normalize a keyword to Eclipse-compatible uppercase form.

        Parameters
        ----------
        keyword : str
            Raw keyword text.

        Returns
        -------
        str
        """
        if not isinstance(keyword, str):
            raise TypeError(f"Keyword must be a string, got {type(keyword)}.")
        return keyword.strip().upper()

    @staticmethod
    def _write_array_raw(
        f: TextIO, 
        keyword: str,
        array: np.ndarray, 
        ncol: int = 20, 
        type: np.dtype = np.float32, 
        decimals: int | None = None
    ) -> TextIO:
        """
        Write an array in plain (non-RLE) GRDECL form.

        Parameters
        ----------
        f : TextIO
            Writable text stream.
        keyword : str
            GRDECL keyword name.
        array : np.ndarray
            Array values to write.
        ncol : int, default=20
            Values per output row.
        type : np.dtype, default=np.float32
            Target dtype before writing.
        decimals : int | None, default=None
            Decimal precision for float formatting.

        Returns
        -------
        TextIO
        """
        flat = np.asarray(array, dtype=type).ravel(order="C")
        keyword = GRDECLWriter._normalize_keyword(keyword)

        fmt = GRDECLWriter._get_fmt(flat, decimals)
        flat2d = flat.reshape(-1, ncol)
        f.write(f"\n{keyword}\n")
        np.savetxt(f, flat2d, fmt=fmt)
        f.write("/\n\n")
        return f
    
    @staticmethod
    def _write_array_rle(
        f: TextIO,
        keyword: str,
        array: np.ndarray,
        ncol: int = 12,
        type: np.dtype = np.float32,
        decimals: int | None = None,
    ) -> TextIO:
        """
        Write an array using run-length encoded GRDECL tokens.

        Parameters
        ----------
        f : TextIO
            Writable text stream.
        keyword : str
            GRDECL keyword name.
        array : np.ndarray
            Array values to encode and write.
        ncol : int, default=12
            Maximum tokens per output line.
        type : np.dtype, default=np.float32
            Target dtype before encoding.
        decimals : int | None, default=None
            Decimal precision used when normalizing floats for equality.

        Returns
        -------
        TextIO
        """
        flat = np.asarray(array, dtype=type).ravel(order="C")

        # For float data, normalize before exact-equality RLE
        if np.issubdtype(flat.dtype, np.floating) and decimals is not None:
            flat = np.round(flat, decimals)

        lengths, values = GRDECLWriter._rle(flat)
        keyword = GRDECLWriter._normalize_keyword(keyword)
        f.write(f"\n{keyword}\n")
        GRDECLWriter._rle_writer(f, lengths, values, ncol)
        f.write("/\n\n")
        return f
            
    @staticmethod
    def _rle_writer(f: TextIO, lengths: np.ndarray, values: np.ndarray, ncol: int = 12) -> None:
        """
        Write precomputed RLE token pairs with line wrapping.

        Parameters
        ----------
        f : TextIO
            Writable text stream.
        lengths : np.ndarray
            Run lengths associated with ``values``.
        values : np.ndarray
            Run values associated with ``lengths``.
        ncol : int, default=12
            Maximum output tokens per line.
        """
        line = []
        for n, v in zip(lengths, values):
            tok = f"{int(n)}*{v}" if n > 1 else f"{v}"
            line.append(tok)
            if len(line) >= ncol:
                f.write(" ".join(line) + "\n")
                line = []
        if line:
            f.write(" ".join(line) + "\n")
        return None

    @staticmethod
    def _rle(flat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Compute run-length encoding using exact equality.

        Parameters
        ----------
        flat : np.ndarray
            Input array flattened to one dimension.

        Returns
        -------
        lengths : np.ndarray
            Run lengths for each consecutive value group.
        values : np.ndarray
            Unique consecutive values from the input array.
        """
        flat = np.asarray(flat).ravel()
        n = flat.size

        if n == 0:
            return np.empty(0, dtype=np.int64), np.empty(0, dtype=flat.dtype)

        change = np.empty(n, dtype=bool)
        change[0] = True
        change[1:] = flat[1:] != flat[:-1]

        starts = np.flatnonzero(change)

        lengths = np.empty(starts.size, dtype=np.int64)
        lengths[:-1] = starts[1:] - starts[:-1]
        lengths[-1] = n - starts[-1]

        return lengths, flat[starts]

    @staticmethod
    def _get_fmt(array: np.ndarray, decimals: int | None) -> str:
        """
        Build the numeric format string for array export.

        Parameters
        ----------
        array : np.ndarray
            Array whose dtype determines integer or float formatting.
        decimals : int | None
            Decimal precision for float formatting.

        Returns
        -------
        str
            Format string compatible with ``numpy.savetxt``.
        """
        fmt = "%d" if is_integer else f"%.{decimals}f" if decimals is not None else "%g"
        return fmt
    
    


