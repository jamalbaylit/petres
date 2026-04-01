"""Interpolation-related error definitions."""

from __future__ import annotations

from typing import ClassVar

from .base import PetresError


class InterpolationError(PetresError):
    """Represent the base exception for interpolation failures.

    This exception is raised for errors encountered during interpolation
    workflows across the project.

    Parameters
    ----------
    message : str or None, default=None
        Error message template. If ``None``, :attr:`default_message` is used.
    **context : object
        Keyword values used to format the resolved message template.

    Notes
    -----
    Message formatting may raise :class:`ValueError` when a required template
    key is missing from ``context``.
    """

    default_message: ClassVar[str] = "An error occurred related to interpolation operations."
