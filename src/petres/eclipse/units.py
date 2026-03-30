from __future__ import annotations

from typing import ClassVar


class UnitConverter:
    """
    Provide unit conversion across supported physical dimensions.

    Units are grouped by physical dimension (e.g., pressure, flowrate).
    Each dimension has a base unit. All conversions are performed
    via that base unit.

    Examples
    --------
    >>> UnitConverter.convert(100, "bar", "psi")
    1450.38
    """

    # Conversion factors TO base unit
    # base unit chosen per dimension
    _UNITS: ClassVar[dict[str, dict[str, float]]] = {
        "pressure": {
            "pa": 1.0,             # base
            "bar": 1e5,
            "psi": 6894.757,
        },
        "flowrate": {
            "sm3/d": 1.0,          # base
            "stb/d": 1 / 6.28981,  # 1 stb = 0.158987 m3
        },
    }

    @classmethod
    def convert(cls, value: float, from_unit: str, to_unit: str) -> float:
        """
        Convert a value between two units of the same physical dimension.

        Parameters
        ----------
        value : float
            Numeric value to convert.
        from_unit : str
            Unit of the input value.
        to_unit : str
            Desired output unit.

        Returns
        -------
        float
            Converted value.

        Raises
        ------
        ValueError
            If units are unknown or belong to different dimensions.
        """

        from_unit = from_unit.lower()
        to_unit = to_unit.lower()

        dimension = cls._find_dimension(from_unit, to_unit)

        units = cls._UNITS[dimension]

        # Convert to base
        value_in_base = value * units[from_unit]

        # Convert from base to target
        return value_in_base / units[to_unit]

    @classmethod
    def _find_dimension(cls, from_unit: str, to_unit: str) -> str:
        """Resolve the physical dimension shared by two unit symbols.

        Parameters
        ----------
        from_unit : str
            Unit symbol for the source value.
        to_unit : str
            Unit symbol for the target value.

        Returns
        -------
        str
            Physical dimension key that contains both units.

        Raises
        ------
        ValueError
            Raised when the units do not belong to the same known dimension.
        """
        for dimension, units in cls._UNITS.items():
            if from_unit in units and to_unit in units:
                return dimension

        raise ValueError(
            f"Incompatible or unknown units: '{from_unit}' → '{to_unit}'"
        )

    @classmethod
    def available_units(cls) -> dict[str, list[str]]:
        """Return all supported unit symbols grouped by physical dimension.

        Returns
        -------
        dict[str, list[str]]
            Mapping of each dimension name to the list of available unit symbols.

        Examples
        --------
        >>> UnitConverter.available_units()["pressure"]
        ['pa', 'bar', 'psi']
        """
        return {
            dim: list(units.keys())
            for dim, units in cls._UNITS.items()
        }