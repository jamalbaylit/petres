"""Grid-related error definitions."""

from ._utils import _iterable_to_str
from .base import PetresError


class GridError(PetresError):
    """Represent a base exception for grid operations.

    This exception groups errors raised by grid creation, transformation,
    validation, and querying workflows.
    """

    default_message: str = "An error occurred related to grid operations."

# ====================================


class UnsupportedGridAttributeError(GridError):
    """Represent an error for unsupported grid attribute access.

    The exception is raised when a requested attribute name is not part of the
    allowed grid attribute set.
    """

    default_message: str = (
        "Unsupported grid attribute '{attribute_name}'. "
        "Supported attributes are: {supported_names}."
    )

    def __init__(self, message: str | None = None, **context: object) -> None:
        """Initialize the exception with optional formatting context.

        Parameters
        ----------
        message : str or None, default=None
            Error message template. If ``None``, the class-level
            ``default_message`` is used.
        **context : object
            Keyword values used for message formatting. If ``supported_names``
            is provided and iterable, it is converted to a readable
            comma-separated string.

        Returns
        -------
        None
            This method initializes the exception instance.

        Notes
        -----
        Any ``supported_names`` value in ``context`` is normalized before
        delegating to :class:`petres.errors.base.PetresError`.

        Examples
        --------
        >>> raise UnsupportedGridAttributeError(
        ...     attribute_name="foo",
        ...     supported_names=["actnum", "coord"]
        ... )
        Traceback (most recent call last):
        ...
        UnsupportedGridAttributeError: Unsupported grid attribute 'foo'. Supported attributes are: actnum, coord.
        """
        if "supported_names" in context:
            context["supported_names"] = _iterable_to_str(context["supported_names"])

        super().__init__(
            message,
            **context
        )
