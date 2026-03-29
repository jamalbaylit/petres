from pathlib import Path
from typing import Generic, Optional, Dict, List
from datetime import datetime
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
    Export corner-point grid to GRDECL format (Schlumberger Petrel / Eclipse).

    Parameters
    ----------
    COORD : np.ndarray
        Shape: (ny + 1, nx + 1, 6)
        Corner-point coordinates array.
    ZCORN : np.ndarray
        Shape: (2 * nz, 2 * ny, 2 * nx)
    ACTNUM : np.ndarray
        Shape: (nz, ny, nx)
    properties : dict[str, np.ndarray], optional
        Cell-based properties.
    """
    
    def __init__(self):
        """
        Initialize exporter with grid arrays.
        
        Parameters:
        - COORD: (Ny, Nx, 2, 3) array of pillar coordinates
        - ZCORN: (Nz, Ny-1, Nx-1, 2, 2, 2) array of corner depths
        - ACTNUM: (Nz, Ny-1, Nx-1) array of active cells
        - properties: Optional dictionary of property arrays {name: array}
        """

    def write_property(
        self,
        path: str | Path,
        *,
        values: np.ndarray,
        keyword: str
    ) -> None:
        """
        Export a single grid property to GRDECL format.
        
        Parameters:
        - path: Output file path
        - values: Array of property values to export
        - keyword: Eclipse keyword for the property (e.g., 'PORO', 'PERMX')
        """
        with open(path, 'w') as f:
            f = GRDECLWriter._write_array(f, keyword, values, rle=True)

    def write(
        self,
        *,
        path: str | Path,
        coord: np.ndarray, 
        zcorn: np.ndarray, 
        actnum: np.ndarray | None = None,
        property_values: Optional[Dict[str, np.ndarray]] = None,
        property_keywords: Optional[List[str]] = None,
        rle: bool = True,
        units: str = "FEET",
        mapunits: str = "FEET",
    ):
        """
        Export grid to GRDECL file.
        
        Parameters:
        - path: Output file path
        - grid_name: Name of the grid
        - project_name: Name of the project
        - user_name: User name for header
        - units: Grid units (FEET or METRES)
        - mapunits: Map units (FEET or METRES)
        - coordsys: Coordinate system specification (handedness, dimension)
        - mapaxes: Map axes specification [x0, y0, x1, y1, x2, y2] (None = auto)
        - include_pinch: Include PINCH keyword
        - format_style: 'columns' (6 per line) or 'single' (1 per line)
        """
        
        ni, nj, nk = zcorn.shape[2], zcorn.shape[1], zcorn.shape[0] // 2

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
                for idx, prop_name in enumerate(property_keywords):
                    prop_array = property_values[idx]
                    f = GRDECLWriter._write_array(f, prop_name, prop_array, rle=rle)


    def _write_header(
        self, 
        f,
        ni: int,
        nj: int,
        nk: int
    ):
        """Write file header with metadata."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d %Y %H:%M:%S")
        f.write(f"-- Format      : Generic Eclipse style (ASCII) grid geometry and properties (*.GRDECL)\n")
        f.write(f"-- Exported by : Petres\n")
        f.write(f"-- Date        : {date_str}\n")
        f.write(f"-- Grid        : 3D Grid ({ni}X{nj}X{nk})\n")
        f.write("\n"*2)
        return f

    def _auto_mapaxes(self):
        """Automatically calculate MAPAXES from grid extent."""
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
    ):  
        
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
        """Normalize property name to valid Eclipse keyword format."""
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
    ) -> None:
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
    ):
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
        """Helper to write RLE data with line wrapping."""
        line = []
        for n, v in zip(lengths, values):
            tok = f"{int(n)}*{v}" if n > 1 else f"{v}"
            line.append(tok)
            if len(line) >= ncol:
                f.write(" ".join(line) + "\n")
                line = []
        if line:
            f.write(" ".join(line) + "\n")
        return f

    @staticmethod
    def _rle(flat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Vectorized run-length encoding using exact equality.

        This is ideal for integer and boolean data. For float data, values should
        usually be normalized beforehand (for example by rounding) so that exact
        equality is meaningful.

        Returns
        -------
        lengths : np.ndarray
            Run lengths.
        values : np.ndarray
            Run values.
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
        is_integer = np.issubdtype(array.dtype, np.integer)
        fmt = "%d" if is_integer else f"%.{decimals}f" if decimals is not None else "%g"
        return fmt
    
    


