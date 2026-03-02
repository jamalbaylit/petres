from enum import Enum
from attr import dataclass
import numpy as np

class WellStatus(str, Enum):
    OPEN = "OPEN"
    STOP = "STOP"
    SHUT = "SHUT"


class WellControlMode(str, Enum):
    # Keep only what you truly support; expand later.
    ORAT = "ORAT"
    WRAT = "WRAT"
    GRAT = "GRAT"
    LRAT = "LRAT"
    CRAT = "CRAT"
    RESV = "RESV"
    BHP  = "BHP"

# class ObservationType(str, Enum):
#     # Keep only what you truly support; expand later.
#     RATE = "RATE"
#     BHP = "PRESSURE"
#     THP = "THP"


@dataclass(frozen=True)
class WCONHISTRecord:
    """
    One WCONHIST row for one well at one time step.

    Use None to mean '*' (ECLIPSE default).
    """
    well_name: str
    well_status: WellStatus = WellStatus.OPEN
    control_mode: WellControlMode = WellControlMode.ORAT
    
    # Targets (depending on mode, only some are used)
    target: float | None = None

class WCONHISTWriter:
    def write(self, path: str, time_steps: list[float], data: np.ndarray):
        # Implement the logic to write WCONHIST format
        pass