from typing import Sequence, Iterable, TextIO
from dataclasses import dataclass
from pathlib import Path
from enum import Enum
import numpy as np
import datetime


class WellStatus(str, Enum):
    """Enumerate allowed well operating statuses for WCONHIST rows."""

    OPEN = "OPEN"
    STOP = "STOP"
    SHUT = "SHUT"


class WellControlMode(str, Enum):
    """Enumerate supported WCONHIST control modes."""

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
    """Represent one WCONHIST row for a single well and date.

    Parameters
    ----------
    well_name : str
        Well name written to the schedule file.
    well_status : WellStatus, default=WellStatus.OPEN
        Operational status associated with this row.
    control_mode : WellControlMode, default=WellControlMode.ORAT
        Target control mode used by the simulator.
    OPR : float or None, default=None
        Observed oil production rate. ``None`` is written as ``"1*"``.
    GPR : float or None, default=None
        Observed gas production rate. ``None`` is written as ``"1*"``.
    WPR : float or None, default=None
        Observed water production rate. ``None`` is written as ``"1*"``.
    THP : float or None, default=None
        Observed tubing head pressure. ``None`` is written as ``"1*"``.
    BHP : float or None, default=None
        Observed bottom-hole pressure. ``None`` is written as ``"1*"``.

    Notes
    -----
    This dataclass is frozen. Field validation runs in ``__post_init__``.
    """
    well_name: str
    well_status: WellStatus = WellStatus.OPEN
    control_mode: WellControlMode = WellControlMode.ORAT

    OPR: float | None = None # Observed Oil Production Rate
    GPR: float | None = None # Observed Gas Production Rate
    WPR: float | None = None # Observed Water Production Rate
    THP: float | None = None # Observed Tubing Head Pressure
    BHP: float | None = None # Observed Bottom Hole Pressure

    def __post_init__(self) -> None:
        """Validate a WCONHIST record after dataclass initialization.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If ``well_name`` is empty.
        TypeError
            If ``well_name`` is not a string.
        """
        if not self.well_name:
            raise ValueError("`well_name` cannot be empty.")
        if not isinstance(self.well_name, str):
            raise TypeError("`well_name` must be a string.")

       
@dataclass(frozen=True)
class WCONHISTStep:
    """Represent one dated schedule step containing WCONHIST records.

    Parameters
    ----------
    date : datetime.datetime
        Timestamp for the schedule step.
    records : tuple[WCONHISTRecord, ...]
        Record collection written under this date.

    Notes
    -----
    The ``records`` tuple must be non-empty and must contain only
    ``WCONHISTRecord`` instances.
    """
    date: datetime.datetime
    records: tuple["WCONHISTRecord", ...]

    def __post_init__(self) -> None:
        """Validate a schedule step after dataclass initialization.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If ``records`` is empty.
        TypeError
            If ``date`` is not a ``datetime.datetime`` instance.
        TypeError
            If any record is not a ``WCONHISTRecord`` instance.
        """
        if not self.records:
            raise ValueError(f"WCONHISTStep({self.date}) must have at least one record.")
        if not isinstance(self.date, datetime.datetime):
            raise TypeError("WCONHISTStep.date must be a datetime.datetime instance.")
        if not all(isinstance(r, WCONHISTRecord) for r in self.records):
            raise TypeError("WCONHISTStep.records must be a tuple of WCONHISTRecord instances.")
        


class WCONHISTWriter:
    """Write WCONHIST schedule text in Eclipse SCHEDULE format.

    Parameters
    ----------
    keyword : str, default="WCONHIST"
        Keyword header emitted for each controls block.
    write_dates : bool, default=True
        Whether to emit ``DATES`` blocks before WCONHIST rows.
    quote_well_names : bool, default=True
        Whether to wrap well names with single quotes.
    float_fmt : str, default="{:.6g}"
        Format specification used for numeric values.
    indent : str, default=" "
        Prefix written at the start of each schedule line.

    Notes
    -----
    The writer maps ``None`` values to ``"1*"`` to preserve Eclipse defaults.
    """

    def __init__(
        self,
        *,
        keyword: str = "WCONHIST",
        write_dates: bool = True,
        quote_well_names: bool = True,
        float_fmt: str = "{:.6g}",
        indent: str = " ",
    ) -> None:
        """Initialize a writer for Eclipse-style WCONHIST schedule blocks.

        Parameters
        ----------
        keyword : str, default="WCONHIST"
            Eclipse keyword to write for history-control rows.
        write_dates : bool, default=True
            Whether to emit a ``DATES`` block before each WCONHIST block.
        quote_well_names : bool, default=True
            Whether to wrap well names in single quotes.
        float_fmt : str, default="{:.6g}"
            Format string used for numeric values.
        indent : str, default=" "
            Prefix written before each schedule row.

        Returns
        -------
        None
        """
        self.keyword = keyword.upper()
        self.write_dates = write_dates
        self.quote_well_names = quote_well_names
        self.float_fmt = float_fmt
        self.indent = indent

    def write(self, path: str | Path, steps: Sequence[WCONHISTStep]) -> None:
        """Write one or more WCONHIST schedule steps to a file.

        Parameters
        ----------
        path : str or pathlib.Path
            Output file path where schedule text will be written.
        steps : Sequence[WCONHISTStep]
            Collection of schedule steps. Steps are sorted by ``date`` before writing.

        Returns
        -------
        None
        """
        assert isinstance(path, (str, Path)), "`path` must be a string or Path instance."
        with open(path, "w", encoding="utf-8") as f:
            # Ensure sorted
            steps_sorted = sorted(steps, key=lambda s: s.date)

            for step in steps_sorted:
                if self.write_dates:
                    self._write_dates_block(f, step.date)
                self._write_wconhist_block(f, step.records)



    def _fmt_value(self, v: float | None) -> str:
        """Format an optional numeric schedule value.

        Parameters
        ----------
        v : float or None
            Numeric value to format. ``None`` is encoded as Eclipse default marker.

        Returns
        -------
        str
            ``"1*"`` when ``v`` is ``None``; otherwise the formatted numeric value.
        """
        if v is None:
            return "1*"
        return self.float_fmt.format(v)

    def _fmt_well(self, name: str) -> str:
        """Format a well name for schedule output.

        Parameters
        ----------
        name : str
            Raw well name.

        Returns
        -------
        str
            Stripped name, optionally surrounded by single quotes.
        """
        name = name.strip()
        if self.quote_well_names:
            return f"'{name}'"
        return name

    def _write_dates_block(self, f: TextIO, d: datetime.datetime | datetime.date) -> None:
        """Write a DATES block for one schedule timestamp.

        Parameters
        ----------
        f : typing.TextIO
            Open text stream receiving schedule output.
        d : datetime.datetime or datetime.date
            Date-like object to serialize in Eclipse DATES format.

        Returns
        -------
        None
        """
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
        """Write one WCONHIST block for a sequence of records.

        Parameters
        ----------
        f : typing.TextIO
            Open text stream receiving schedule output.
        records : Iterable[WCONHISTRecord]
            History-control rows to serialize.

        Returns
        -------
        None
        """
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