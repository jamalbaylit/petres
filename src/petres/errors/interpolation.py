from __future__ import annotations

"""Interpolation-related error definitions."""

from .base import PetresError


class InterpolationError(PetresError):
    """Signal failures raised by interpolation workflows.

    Use this exception as the common base for interpolation-specific errors.
    """

    default_message: str = "An error occurred related to interpolation operations."
