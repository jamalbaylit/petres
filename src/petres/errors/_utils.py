"""Utility helpers for formatting error messages."""

from collections.abc import Iterable

def _iterable_to_str(value) -> str:
    """Convert an iterable to a readable, comma-separated string.

    Parameters
    ----------
    value : Any
        Iterable to stringify; strings are returned unchanged.

    Returns
    -------
    str
        Comma-separated representation, or empty string for ``None``.
    """
    # None → empty string (optional choice)
    if value is None:
        return ""

    # Strings should NOT be treated as iterable of chars
    if isinstance(value, str):
        return value

    # Handle sets → sorted for deterministic output
    if isinstance(value, set):
        value = sorted(value)

    # Handle general iterables (list, tuple, numpy arrays, etc.)
    if isinstance(value, Iterable):
        try:
            return ", ".join(map(str, value))
        except TypeError:
            pass

    # Fallback for everything else
    return str(value)