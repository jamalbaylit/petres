from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Literal
import numpy as np


@dataclass(frozen=True)
class CellProperty:
    """
    Cell-based property defined on a (nk, nj, ni) grid.

    values can be:
      - 3D array: (nk, nj, ni)
      - 1D array: (nk*nj*ni,) with dims provided
    """
    values: np.ndarray
    eclipse_keyword: Optional[str] = None                 # Eclipse keyword (PORO, PERMX, ...)
    name: Optional[str] = None
    description: Optional[str] = None

    def __post_init__(self):
        assert isinstance(self.values, np.ndarray), f"values must be a numpy array, got {type(self.values)}"
        assert self.values.ndim == 3, f"Values must be 3D, got shape {self.values.shape}"
        # make sure keyword has zero space or tab etc.
        if self.eclipse_keyword is not None:
            assert self.eclipse_keyword.strip() == self.eclipse_keyword, f"`eclipse_keyword` must not have leading/trailing whitespace, got '{self.eclipse_keyword}'"
            self.eclipse_keyword = self.eclipse_keyword.upper()

    @property
    def shape(self) -> Tuple[int, int, int]:
        return self.values.shape

    @property
    def nk(self) -> int: return self.shape[0]

    @property
    def nj(self) -> int: return self.shape[1]
    
    @property
    def ni(self) -> int: return self.shape[2]
    
    @property
    def n_cells(self) -> int: return self.nk * self.nj * self.ni


