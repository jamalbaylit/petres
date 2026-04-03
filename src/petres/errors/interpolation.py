from __future__ import annotations

"""Interpolation-related error definitions."""

from .base import PetresError


class InterpolationError(PetresError):
    """Signal failures raised by interpolation workflows.

    Use this exception as the common base for interpolation-specific errors.

    Attributes
    ----------
    default_message : str
        Fallback error message used when no explicit message is provided.
    """

    default_message: str = "An error occurred related to interpolation operations."
