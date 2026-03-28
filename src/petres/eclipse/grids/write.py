from pathlib import Path
from typing import Generic, Optional, Dict, List
from datetime import datetime
from typing import TextIO
import numpy as np

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

        
    def write(
        self,
        *,
        path: str | Path,
        coord: np.ndarray, 
        zcorn: np.ndarray, 
        actnum: np.ndarray,
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
        
        nk, nj, ni = actnum.shape

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
            f.write("SPECGRID\n")
            f.write(f"{ni} {nj} {nk}  1  F /\n")
            
            # COORD
            f = self._write_coord(f, coord)
            
            # ZCORN
            f = self._write_zcorn(f, zcorn)
            
            # ACTNUM
            f  = self._write_actnum(f, actnum)
            
            # Properties
            # for prop_name, prop_array in self.properties.items():
            #     self._write_property(f, prop_name, prop_array, format_style)
        
    def _array_to_string(self, arr: np.ndarray, ncol: int = 8) -> str:
        """Convert a numpy array to a formatted string."""
        flat = arr.ravel(order="C")
        flat2d = flat.reshape(-1, ncol)
        return "\n".join(" ".join(f"{x:.8f}" for x in row) for row in flat2d)
    


    

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
    def _write_coord(
        f: TextIO,
        coord: np.ndarray,
        ncol: int = 6,
    ):
        """
        coord shape: (ny+1, nx+1, 6)
        """

        # Flatten in Eclipse order
        flat = coord.reshape(-1, ncol)

        f.write("COORD\n")
        np.savetxt(
            f,
            flat,
            fmt="%.8f",
        )
        f.write("/\n\n")
        return f
        
    @staticmethod
    def _write_zcorn(
        f: TextIO,
        zcorn: np.ndarray,
        ncol: int = 8,
    ):
        """
        zcorn shape: (2*nz, 2*ny, 2*nx)
        """
        # Eclipse requires Fortran ordering
        flat = zcorn.reshape(-1, ncol)

        f.write("ZCORN\n")
        np.savetxt(
            f,
            flat,  # savetxt wants 2D
            fmt="%.8f",
        )
        f.write("/\n\n")
        return f
    
    @staticmethod
    def _write_actnum(
        f: TextIO,
        actnum: np.ndarray,
        *,
        compress: bool = True,
        ncol: int = 20,
        tokens_per_line: int = 12,
    ) -> None:
        if compress:
            f = GRDECLWriter._write_actnum_rle(f, actnum, tokens_per_line=tokens_per_line)
        else:
            f = GRDECLWriter._write_actnum_raw(f, actnum, ncol=ncol)
        return f

    @staticmethod
    def _write_actnum_raw(f: TextIO, actnum: np.ndarray, ncol: int = 20) -> None:
        flat = np.asarray(actnum, dtype=np.int8).ravel(order="C")
        flat2d = flat.reshape(-1, ncol)
        f.write("ACTNUM\n")
        np.savetxt(f, flat2d, fmt="%d")
        f.write("/\n\n")
        return f
        
    @staticmethod
    def _write_actnum_rle(
        f: TextIO,
        active: np.ndarray,
        tokens_per_line: int = 12,
    ) -> None:
        flat = np.asarray(active, dtype=np.bool_).ravel(order="C").astype(np.int8)

        lengths, values = GRDECLWriter._rle_01(flat)

        f.write("ACTNUM\n")

        # line wrap
        line = []
        for n, v in zip(lengths, values):
            tok = f"{int(n)}*{int(v)}" if n > 1 else f"{int(v)}"
            line.append(tok)
            if len(line) >= tokens_per_line:
                f.write(" ".join(line) + "\n")
                line = []
        if line:
            f.write(" ".join(line) + "\n")
        f.write("/\n\n")
        return f

    @staticmethod
    def _rle_01(flat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Vectorized RLE for 0/1 array.
        Returns (lengths, values).
        """
        flat = np.asarray(flat, dtype=np.int8)
        if flat.size == 0:
            return np.array([], dtype=np.int64), np.array([], dtype=np.int8)

        # indices where value changes
        change_idx = np.flatnonzero(np.diff(flat)) + 1
        starts = np.r_[0, change_idx]
        ends = np.r_[change_idx, flat.size]

        lengths = ends - starts
        values = flat[starts]
        return lengths.astype(np.int64), values






    @staticmethod
    def _write_property(f, prop_name, prop_array, format_style="%.6f", ncol: int = 6):
        """
        Write a cell-based property array to GRDECL file.

        prop_array shape: (Nz, Ny, Nx)
        Ordering: i fastest, then j, then k (Fortran order)
        """

        f.write(f"\n{prop_name.upper()}\n")

        expected_shape = (self.Nz, self.Ny_cells, self.Nx_cells)
        if prop_array.shape != expected_shape:
            raise ValueError(
                f"Property '{prop_name}' has incorrect shape {prop_array.shape}, "
                f"expected {expected_shape}"
            )

        # Replace NaNs (no copy if possible)
        if np.issubdtype(prop_array.dtype, np.floating):
            data = np.nan_to_num(prop_array, nan=0.0, copy=False)
        else:
            data = prop_array

        # Eclipse flattening
        flat = data.reshape(-1, ncol)

        # Integer vs float formatting
        is_integer = np.issubdtype(flat.dtype, np.integer)
        fmt = "%d" if is_integer else format_style

        # Write efficiently (single buffered call)
        np.savetxt(
            f,
            flat[np.newaxis],   # savetxt requires 2D
            fmt=fmt,
        )

        f.write("\n/\n")
    
    def _write_array(self, f, values, format_style, is_integer=False):
        """Write array values with proper formatting."""
        
        if format_style == "columns":
            # Write 6 values per line (standard Eclipse format)
            values_per_line = 6
            
            for i, val in enumerate(values):
                if i > 0 and i % values_per_line == 0:
                    f.write("\n")
                
                if is_integer:
                    f.write(f"{int(val):8d} ")
                else:
                    # Use scientific notation for better precision
                    f.write(f"{val:14.6e} ")
            
            f.write("\n")
        
        elif format_style == "single":
            # Write one value per line
            for val in values:
                if is_integer:
                    f.write(f"{int(val)}\n")
                else:
                    f.write(f"{val:.6e}\n")
        
        else:
            raise ValueError(f"Unknown format_style: {format_style}")
    
    def add_property(self, name: str, array: np.ndarray):
        """
        Add a property to be exported.
        
        Parameters:
        - name: Property name (e.g., 'PORO', 'PERMX', 'SATW')
        - array: (Nz, Ny_cells, Nx_cells) array of property values
        """
        if array.shape != (self.Nz, self.Ny_cells, self.Nx_cells):
            raise ValueError(
                f"Property array has incorrect shape {array.shape}, "
                f"expected ({self.Nz}, {self.Ny_cells}, {self.Nx_cells})"
            )
        self.properties[name] = array
    
    def remove_property(self, name: str):
        """Remove a property from export."""
        if name in self.properties:
            del self.properties[name]
    
    def list_properties(self):
        """List all properties that will be exported."""
        return list(self.properties.keys())


