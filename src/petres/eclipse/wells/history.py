from typing import Sequence, Iterable, TextIO
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import numpy as np
import datetime

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

    OPR: float | None = None # Observed Oil Production Rate
    GPR: float | None = None # Observed Gas Production Rate
    WPR: float | None = None # Observed Water Production Rate
    THP: float | None = None # Observed Tubing Head Pressure
    BHP: float | None = None # Observed Bottom Hole Pressure

    def __post_init__(self):
        if not self.well_name:
            raise ValueError("`well_name` cannot be empty.")
        if not isinstance(self.well_name, str):
            raise TypeError("`well_name` must be a string.")

       
@dataclass(frozen=True)
class WCONHISTStep:
    """
    A dated schedule step that applies WCONHIST controls to multiple wells.
    """
    date: datetime.datetime
    records: tuple["WCONHISTRecord", ...]

    def __post_init__(self):
        if not self.records:
            raise ValueError(f"WCONHISTStep({self.date}) must have at least one record.")
        if not isinstance(self.date, datetime.datetime):
            raise TypeError("WCONHISTStep.date must be a datetime.datetime instance.")
        if not all(isinstance(r, WCONHISTRecord) for r in self.records):
            raise TypeError("WCONHISTStep.records must be a tuple of WCONHISTRecord instances.")
        


class WCONHISTWriter:
    """
    Write WCONHIST blocks (and optionally DATES) in ECLIPSE SCHEDULE format.

    Design goals:
    - User passes typed records (safe, validated).
    - Writer emits correct ECLIPSE text.
    - None -> '*' mapping is consistent.
    """

    def __init__(
        self,
        *,
        keyword: str = "WCONHIST",
        write_dates: bool = True,
        quote_well_names: bool = True,
        float_fmt: str = "{:.6g}",
        indent: str = " ",
    ):
        self.keyword = keyword.upper()
        self.write_dates = write_dates
        self.quote_well_names = quote_well_names
        self.float_fmt = float_fmt
        self.indent = indent

    def write(self, path: str | Path, steps: Sequence[WCONHISTStep]) -> TextIO:
        assert isinstance(path, (str, Path)), "`path` must be a string or Path instance."
        with open(path, "w", encoding="utf-8") as f:
            # Ensure sorted
            steps_sorted = sorted(steps, key=lambda s: s.date)

            for step in steps_sorted:
                if self.write_dates:
                    self._write_dates_block(f, step.date)
                self._write_wconhist_block(f, step.records)
            return f



    def _fmt_value(self, v: float | None) -> str:
        if v is None:
            return "1*"
        return self.float_fmt.format(v)

    def _fmt_well(self, name: str) -> str:
        name = name.strip()
        if self.quote_well_names:
            return f"'{name}'"
        return name

    def _write_dates_block(self, f: TextIO, d: datetime.datetime | datetime.date) -> None:
        # day: An integer between 1 and 31
        # months: JAN, FEB, MAR, APR, MAY, JUN, JLY, AUG, SEP, OCT, NOV or DEC
        # year: 4 digit integer
        # time: HH:MM:SS.SSSS

        mon = d.strftime("%b").upper()  # JAN, FEB...
        f.write("DATES\n")
        date = f"{d.day} {mon} {d.year}"
        if isinstance(d, datetime.datetime):
            f.write(f"{self.indent}{date} {d.hour:02d}:{d.minute:02d}:{d.second:02d}.{d.microsecond:04d}/\n")
        elif isinstance(d, datetime.date):
            f.write(f"{self.indent}{date} /\n")
        f.write("/\n\n")

    def _write_wconhist_block(self, f: TextIO, records: Iterable[WCONHISTRecord]) -> None:
        f.write(f"{self.keyword}\n")
        for r in records:
            # Typical WCONHIST shape in many decks:
            # 'WELL'  OPEN  ORAT  <orat> <wrat> <grat> <lrat> <resv> <bhp> <thp> /
            # In practice, the exact columns vary by simulator version/options,
            # but this fixed-column approach is stable if YOU commit to it in your API.
            cols = [
                self._fmt_well(r.well_name),
                r.well_status,
                r.control_mode,
                self._fmt_value(r.OPR),
                self._fmt_value(r.WPR),
                self._fmt_value(r.GPR),
                "1*",
                "1*",
                self._fmt_value(r.THP),
                self._fmt_value(r.BHP),
                "/",
            ]
            f.write(self.indent + "  ".join(cols) + "\n")
        f.write("/\n\n")