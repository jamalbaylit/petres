from __future__ import annotations

from typing import Final


# List of keywords that will be skipped when looking for property data
NOT_PROPERTY_KEYWORDS: Final[set[str]] = {"COORD", "ZCORN", "SPECGRID", "MAPAXES", "NOECHO", "ECHO", "MAPUNITS", "GRIDUNIT", "GDORIENT", "INC", "DEC", "FAULTS"}

"""Keyword descriptions for Eclipse grid cell properties."""
CELL_KEYWORDS: Final[dict[str, str]] = {
    # --- Rock Properties ---
    "PORO": "Porosity of each grid cell (fraction, 0–1).",
    "PERMX": "Permeability in X direction (mD).",
    "PERMY": "Permeability in Y direction (mD).",
    "PERMZ": "Permeability in Z direction (mD).",
    "NTG": "Net-to-gross ratio (fraction of active rock).",
    "MULTPV": "Pore volume multiplier.",
    "MULTX": "Transmissibility multiplier in X direction.",
    "MULTY": "Transmissibility multiplier in Y direction.",
    "MULTZ": "Transmissibility multiplier in Z direction.",

    # --- Initial Conditions ---
    "PRESSURE": "Initial reservoir pressure (per cell).",
    "SWAT": "Initial water saturation.",
    "SOIL": "Initial oil saturation.",
    "SGAS": "Initial gas saturation.",
    "RS": "Solution gas-oil ratio per cell.",
    "RV": "Vaporized oil-gas ratio per cell.",

    # --- Rock Regions ---
    "SATNUM": "Saturation function region number.",
    "PVTNUM": "PVT region number.",
    "ROCKNUM": "Rock compressibility region number.",
    "EQLNUM": "Equilibration region number.",
    "FLUXNUM": "Flux region number.",
    "MULTNUM": "Transmissibility multiplier region number.",

    # --- Geometry / Activity ---
    "ACTNUM": "Active/inactive cell flag (1=active, 0=inactive).",
    "DZ": "Cell thickness in Z direction.",
    "DX": "Cell length in X direction.",
    "DY": "Cell length in Y direction.",

    # --- Thermal (if thermal simulation) ---
    "TEMP": "Initial temperature per cell.",
    "THCONR": "Rock thermal conductivity.",
    "THCROCK": "Rock heat capacity.",

    # --- Special / Advanced ---
    "FIPNUM": "Fluid-in-place region number.",
    "IMBNUM": "Imbibition region number.",
    "OPERNUM": "Operational region number.",
}