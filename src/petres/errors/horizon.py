"""Horizon-related error definitions."""

from __future__ import annotations

from .base import PetresError


class HorizonError(PetresError):
    """Represent errors raised during horizon operations.

    Use this exception to distinguish horizon-specific failures from other
    domain errors and handle them consistently.

    Attributes
    ----------
    default_message : str
        Fallback message used when an explicit message is not provided by the
        caller.
    """

    default_message: str = "An error occurred related to horizon operations."
