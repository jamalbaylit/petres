import numpy as np
import re

class GRDECLReader():
    """
    Reads GRDECL (ECLIPSE) grid files and extracts:
    - NX, NY, NZ (dimensions)
    - COORD
    - ZCORN
    - ACTNUM (optional)
    """

    # ============================================================
    # Public API
    # ============================================================

    def clean_comments(self, text):
        # Remove comments (lines starting with --)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            if '--' in line:
                index = line.index('--')
                line = line[:index]
            cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)
    

    def read(self, path):
        with open(path, "r") as f:
            text = f.read()
        text = self.clean_comments(text)
        # Extract dimensions
        dim = self._get_keyword_array(text, "SPECGRID", dtype=str)
        nx, ny, nz = int(dim[0]), int(dim[1]), int(dim[2])

        # Extract COORD array
        coord = self._get_keyword_array(text, "COORD")
        expected_coord_size = (nx + 1) * (ny + 1) * 6
        if len(coord) != expected_coord_size:
            raise ValueError(f"COORD array size mismatch: expected {expected_coord_size}, got {len(coord)}")
        # COORD is ordered as: for each pillar (j-direction inner loop), 6 values
        coord = coord.reshape((ny + 1, nx + 1, 6))

        # Extract ZCORN array
        zcorn = self._get_keyword_array(text, "ZCORN")
        expected_zcorn_size = nx * ny * nz * 8
        if len(zcorn) != expected_zcorn_size:
            raise ValueError(f"ZCORN array size mismatch: expected {expected_zcorn_size}, got {len(zcorn)}")
        # ZCORN ordering: for each layer k, for each j, for each i, 4 values (top face)
        # then repeat for bottom face. Reshape to (nz, 2, ny, 2, nx, 2)
        # Standard Eclipse ordering: cycles through X fastest, then Y, then Z
        zcorn = zcorn.reshape((2*nz, 2*ny, 2*nx))

        # ACTNUM is optional
        try:
            actnum = self._get_keyword_array(text, "ACTNUM", dtype=int)
            expected_actnum_size = nx * ny * nz
            if len(actnum) != expected_actnum_size:
                raise ValueError(f"ACTNUM array size mismatch: expected {expected_actnum_size}, got {len(actnum)}")
            # ACTNUM ordering: X varies fastest, then Y, then Z
            actnum = actnum.reshape((nz, ny, nx))
        except (ValueError, AssertionError):
            actnum = None

        return {
            "NX": nx,
            "NY": ny,
            "NZ": nz,
            "COORD": coord,
            "ZCORN": zcorn,
            "ACTNUM": actnum,
        }


    @staticmethod
    def _find_keyword_line(text, keyword):
        pattern = rf"^[ \t]*{re.escape(keyword)}.*$"
        matches = list(re.finditer(pattern, text, flags=re.MULTILINE))

        if not matches:
            return None

        last_match = matches[-1]
        # end position of the matched line
        end_pos = last_match.end()

        # return everything after the matched line
        return text[end_pos:]

    @staticmethod
    def _extract_text_till_slash(text):
        """
        Extract substring from start of the line until the first "/".
        Returns the part before "/", or the whole line if "/" does not exist.
        """
        idx = text.find("/")
        assert idx != -1, f"No '/' found in line: {text}"
        return text[:idx]
        
        
        
    @staticmethod
    def _get_keyword_content(text, keyword):
        """
        Finds single value keywords like:

        NX
            30 /
        """
        print("Looking for keyword:", keyword)
        text_cropped = GRDECLReader._find_keyword_line(text, keyword)
        if not text_cropped:
            raise ValueError(f"{keyword} not found in GRDECL file.")
        data = GRDECLReader._extract_text_till_slash(text_cropped)
        data = re.sub(r'\s+', ' ', data).strip()
        return data

    @staticmethod
    def _expand_ecl_pattern(text):
        pattern = re.compile(r'(\d+)\*([^\s]+)')  # matches NUM*VALUE

        def repl(m):
            num = int(m.group(1))
            val = m.group(2)
            return " ".join([val] * num)

        return pattern.sub(repl, text)

    @staticmethod
    def _get_keyword_array(text, keyword, dtype=float):
        content = GRDECLReader._get_keyword_content(text, keyword)
        data = GRDECLReader._expand_ecl_pattern(content)
        return np.array(data.split(), dtype=dtype)
  