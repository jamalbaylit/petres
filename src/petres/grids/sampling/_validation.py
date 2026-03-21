import numpy as np

def _validate_vertex_array(arr: np.ndarray, name: str) -> np.ndarray:
    try:
        arr = np.asarray(arr, dtype=float)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to convert '{name}' to a float array: {e}") from e


    if arr.ndim != 1:
        raise ValueError(f"'{name}' must be a 1D array.")
    if arr.size < 2:
        raise ValueError(f"'{name}' must contain at least 2 vertex values.")
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"'{name}' contains NaN or inf.")
    if np.any(np.diff(arr) <= 0):
        raise ValueError(f"'{name}' must be strictly increasing.")
    return arr