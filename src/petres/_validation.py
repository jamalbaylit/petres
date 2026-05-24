"""Small validation helpers shared across the package."""

import numpy as np

def _validate_z_scale(value: float, name: str = "z_scale") -> float:
    """Validate and coerce z_scale to a positive finite float.

    Parameters
    ----------
    value : float
        Candidate z_scale value.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    float
        The validated z_scale.

    Raises
    ------
    ValueError
        If conversion fails, the value is not finite, or it is non-positive.
    """
    v = _validate_positive_float(value, name)
    return v

def _validate_positive_float(value: float, name: str) -> float:
    """Validate and coerce a value to a positive finite float.

    Parameters
    ----------
    value : float
        Candidate numeric value.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    float
        The validated positive float.

    Raises
    ------
    ValueError
        If conversion fails, the value is not finite, or it is non-positive.
    """
    v = _validate_finite_float(value, name)
    if v <= 0:
        raise ValueError(f"`{name}` must be positive, got {v}.")
    return v

def _validate_positive_int(value: int, name: str) -> int:
    """Validate and coerce a value to a positive integer.

    Parameters
    ----------
    value : int
        Candidate integer value.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    int
        The validated positive integer.

    Raises
    ------
    ValueError
        If conversion fails or the value is not a positive integer.
    """
    try:
        v = int(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"`{name}` must be an integer, got {type(value).__name__}.") from e

    if v <= 0:
        raise ValueError(f"`{name}` must be a positive integer, got {v}.")
    return v


def _validate_finite_float(value: float, name: str) -> float:
    """Coerce a numeric input to ``float`` and ensure it is finite.

    Parameters
    ----------
    value : float
        Candidate numeric value.
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
        raise ValueError(f"'{name}' must be a real number, got {type(value).__name__}.") from e

    if not np.isfinite(v):
        raise ValueError(f"'{name}' must be finite.")
    return v

def _validate_nonempty_string(value: str, name: str) -> str:
    """Ensure a string is non-empty and trimmed.

    Parameters
    ----------
    value : str
        Candidate string value.
    name : str
        Parameter name used in error messages.

    Returns
    -------
    str
        The validated string.

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


