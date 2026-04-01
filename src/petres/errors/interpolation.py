"""Interpolation-related error definitions."""

from .base import PetresError


class InterpolationError(PetresError):
    """Represent the base exception for interpolation failures.

    This exception is raised for errors encountered during interpolation
    workflows across the project.

    Attributes
    ----------
    default_message : str
        Fallback error message used when no explicit message is provided.
    """

    default_message: str = "An error occurred related to interpolation operations."
