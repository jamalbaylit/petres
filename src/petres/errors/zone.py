from __future__ import annotations

"""Zone-related error definitions."""

from .base import PetresError


class ZoneError(PetresError):
    """Represent errors raised during zone operations.

    Use this exception to distinguish zone-specific failures from other domain
    errors and handle them consistently.

    Attributes
    ----------
    default_message : str
        Fallback message used when an explicit message is not provided.
    """

    default_message: str = "An error occurred related to zone operations."
