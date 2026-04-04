from __future__ import annotations

from typing import Any

"""Grid-related error definitions."""

from ._utils import _iterable_to_str
from .base import PetresError


class GridError(PetresError):
    """Represent the base exception for grid-related failures."""

    default_message: str = "An error occurred related to grid operations."

# ====================================


class UnsupportedGridAttributeError(GridError):
    """Represent an error for unsupported grid attribute access.

    Parameters
    ----------
    message : str | None, default=None
        Error message template. If ``None``, the class-level
        ``default_message`` is used.
    **context : Any
        Keyword values used for message formatting. If ``supported_names`` is
        provided and iterable, it is converted to a readable
        comma-separated string.
    """

    default_message: str = (
        "Unsupported grid attribute '{attribute_name}'. "
        "Supported attributes are: {supported_names}."
    )

    def __init__(self, message: str | None = None, **context: Any) -> None:
        """Initialize the exception with optional formatting context."""
        if "supported_names" in context:
            context["supported_names"] = _iterable_to_str(context["supported_names"])

        super().__init__(
            message,
            **context
        )
