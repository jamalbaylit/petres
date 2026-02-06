from typing import Optional, Dict, List
from datetime import datetime
from typing import TextIO
import numpy as np

class GRDECLWriter:
    """
    Export corner-point grid to GRDECL format (Schlumberger Petrel / ECLIPSE).

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
    
    def __init__(self, COORD, ZCORN, ACTNUM, properties: Optional[Dict[str, np.ndarray]] = None):
        """
        Initialize exporter with grid arrays.
        
        Parameters:
        - COORD: (Ny, Nx, 2, 3) array of pillar coordinates
        - ZCORN: (Nz, Ny-1, Nx-1, 2, 2, 2) array of corner depths
        - ACTNUM: (Nz, Ny-1, Nx-1) array of active cells
        - properties: Optional dictionary of property arrays {name: array}
        """
        self.COORD = COORD
        self.ZCORN = ZCORN
        self.ACTNUM = ACTNUM
        self.properties = properties or {}
        
        self.Nz, self.Ny_cells, self.Nx_cells = ACTNUM.shape
        self.Ny, self.Nx = COORD.shape[:2]
        
    def write(
        self,
        filename: str,
        grid_name: str = "3D Grid",
        project_name: str = "Grid Project",
        user_name: str = "User",
        units: str = "FEET",
        mapunits: str = "FEET",
        coordsys: tuple = (1, 12),
        mapaxes: Optional[List[float]] = None,
        include_pinch: bool = True,
        format_style: str = "columns"
    ):
        """
        Export grid to GRDECL file.
        
        Parameters:
        - filename: Output file path
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
        
        with open(filename, 'w') as f:
            # Header
            self._write_header(f, grid_name, project_name, user_name)
            
            # Keywords
            f.write("\nNOECHO\n")
            
            if include_pinch:
                f.write("PINCH\n/\n")
            
            # Map units
            f.write(f"MAPUNITS\n'{mapunits}' /\n")
            
            # Map axes
            if mapaxes is not None:
                # mapaxes = self._auto_mapaxes()
                f.write(f"MAPAXES\n")
                f.write(f"{mapaxes[0]:.6f} {mapaxes[1]:.6f}\n")
                f.write(f"{mapaxes[2]:.6f} {mapaxes[3]:.6f}\n")
                f.write(f"{mapaxes[4]:.6f} {mapaxes[5]:.6f} /\n")
            
            # Grid units
            f.write(f"GRIDUNIT\n'{units}' /\n")
            
            # SPECGRID
            f.write("SPECGRID\n")
            f.write(f"{self.Nx_cells} {self.Ny_cells} {self.Nz}  1  F /\n")
            
            # COORDSYS
            f.write("\nCOORDSYS\n")
            f.write(f"{coordsys[0]} {coordsys[1]} /\n")
            
            # COORD
            self._write_coord(f, self.COORD, self.Nx_cells, self.Ny_cells)
            
            # ZCORN
            self._write_zcorn(f, self.ZCORN, self.Nx_cells, self.Ny_cells, self.Nz)
            
            # ACTNUM
            self._write_actnum(f, self.ACTNUM, self.Nx_cells, self.Ny_cells, self.Nz)
            
            # Properties
            for prop_name, prop_array in self.properties.items():
                self._write_property(f, prop_name, prop_array, format_style)
        





        print(f"GRDECL file exported to: {filename}")
    
    def _write_header(self, f, grid_name, project_name, user_name):
        """Write file header with metadata."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d %Y %H:%M:%S")
        
        f.write(f"-- Format      : Generic ECLIPSE style (ASCII) grid geometry and properties (*.GRDECL)\n")
        f.write(f"-- Exported by : Python Grid Builder\n")
        f.write(f"-- User name   : {user_name}\n")
        f.write(f"-- Date        : {date_str}\n")
        f.write(f"-- Project     : {project_name}\n")
        f.write(f"-- Grid        : {grid_name} ({self.Nx_cells}X{self.Ny_cells}X{self.Nz})\n")
        f.write(f"--\n")
        f.write(f"-- Grid dimensions:\n")
        f.write(f"--   NX (I-direction): {self.Nx_cells}\n")
        f.write(f"--   NY (J-direction): {self.Ny_cells}\n")
        f.write(f"--   NZ (K-direction): {self.Nz}\n")
        f.write(f"--   Total cells: {self.Nx_cells * self.Ny_cells * self.Nz}\n")
        f.write(f"--   Active cells: {self.ACTNUM.sum()}\n")
    
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
        nx: int,
        ny: int,
        ncol: int = 6,
    ):
        """
        coord shape: (ny+1, nx+1, 6)
        """

        coord = coord.reshape((ny + 1, nx + 1, 6))

        # Flatten in ECLIPSE order
        flat = coord.reshape(-1, ncol)

        f.write("COORD\n")
        np.savetxt(
            f,
            flat,
            fmt="%.8f",
        )
        f.write("/\n\n")
        
    @staticmethod
    def _write_zcorn(
        f: TextIO,
        zcorn: np.ndarray,
        nx: int,
        ny: int,
        nz: int,
        ncol: int = 8,
    ):
        """
        zcorn shape: (2*nz, 2*ny, 2*nx)
        """

        zcorn = zcorn.reshape((2 * nz, 2 * ny, 2 * nx))

        # ECLIPSE requires Fortran ordering
        # flat = zcorn.ravel(order="F")
        flat = zcorn.reshape(-1, ncol)

        f.write("ZCORN\n")
        np.savetxt(
            f,
            flat,  # savetxt wants 2D
            fmt="%.8f",
        )
        f.write("/\n\n")
    
    @staticmethod
    def _write_actnum(
        f: TextIO,
        actnum: np.ndarray,
        nx: int,
        ny: int,
        nz: int,
        ncol: int = 1,
    ):
        """
        actnum shape: (nz, ny, nx)
        """

        actnum = actnum.reshape((nz, ny, nx))

        # ECLIPSE expects Fortran order
        flat = actnum.reshape(-1, ncol)
        # flat = actnum.ravel(order="F")

        f.write("ACTNUM\n")
        np.savetxt(
            f,
            flat,   # savetxt needs 2D
            fmt="%d",
        )
        f.write("/\n\n")

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

        # ECLIPSE flattening
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
            # Write 6 values per line (standard ECLIPSE format)
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


