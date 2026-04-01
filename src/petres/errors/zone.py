"""Zone-related error definitions."""

from __future__ import annotations

from typing import ClassVar

from petres.errors.base import PetresError


class ZoneError(PetresError):
    """Represent errors raised during zone operations.

    This exception provides a zone-specific error type so callers can catch
    and handle failures that occur in zone modeling and processing workflows.

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

    default_message: ClassVar[str] = "An error occurred related to zone operations."
