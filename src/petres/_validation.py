"""Small validation helpers shared across the package."""

from __future__ import annotations

import numpy as np


def _validate_finite_float(value: float, name: str) -> float:
    """Coerce a numeric input to ``float`` and ensure it is finite.

    Parameters
    ----------
    value : float
        Candidate numeric value. Must be convertible to ``float``.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    float
        The validated finite float.

    Raises
    ------
    ValueError
        If conversion fails or the value is not finite.
    """
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"'{name}' must be a real number")

    if not np.isfinite(v):
        raise ValueError(f"'{name}' must be finite.")
    return v


def _validate_nonempty_string(value: str, name: str) -> str:
    """Ensure a string is non-empty and free of surrounding whitespace.

    Parameters
    ----------
    value : str
        Candidate string. Must not be empty or have leading/trailing whitespace.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    str
        The validated string, unchanged.

    Raises
    ------
    TypeError
        If ``value`` is not a string.
    ValueError
        If the string is empty or contains leading/trailing whitespace.
    """
    if not isinstance(value, str):
        raise TypeError(f"`{name}` must be a string.")
    if value == "":
        raise ValueError(f"`{name}` cannot be empty.")
    if value != value.strip():
        raise ValueError(f"`{name}` cannot have leading or trailing whitespace.")
    return value