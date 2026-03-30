"""Zone-related error definitions."""

from petres.errors.base import PetresError


class ZoneError(PetresError):
    """Represent errors raised during zone operations.

    This exception provides a zone-specific error type so callers can catch
    and handle failures that occur in zone modeling and processing workflows.

    Attributes
    ----------
    default_message : str
        Fallback message used when an explicit message is not provided.
    """

    default_message: str = "An error occurred related to zone operations."
