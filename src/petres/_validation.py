import numpy as np

def _validate_finite_float(value, name: str) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        raise ValueError(f"'{name}' must be a real number: {e}") from e

    if not np.isfinite(v):
        raise ValueError(f"'{name}' must be finite.")

    return v