import numpy as np

def _validate_finite_float(value: float, name: str) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"'{name}' must be a real number")

    if not np.isfinite(v):
        raise ValueError(f"'{name}' must be finite.")
    return v

def _validate_nonempty_string(value: str, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"`{name}` must be a string.")
    if value == "":
        raise ValueError(f"`{name}` cannot be empty.")
    if value != value.strip():
        raise ValueError(f"`{name}` cannot have leading or trailing whitespace.")
    return value