"""Property-related error definitions."""

from typing import Any

from ._utils import _iterable_to_str
from .base import PetresError


class PropertyError(PetresError):
    """Define the base exception type for property modeling failures.

    This class specializes :class:`PetresError` for property-modeling related
    failures and serves as a common ancestor for more specific property error
    types.

    Attributes
    ----------
    default_message : str
        Fallback error message template used when no explicit message is
        provided.
    """

    default_message = "An error occurred related to property operations."

# ====================================

class MissingEclipseKeywordError(PropertyError):
    """Signal that a property is missing an Eclipse export keyword.

    This exception is raised when a property must be exported to Eclipse format
    but does not define the required keyword identifier.

    Attributes
    ----------
    default_message : str
        Message template with the missing property name placeholder.
    """

    default_message = (
        "Property '{property_name}' does not have an associated Eclipse keyword. "
        "Make sure to define the property with an `eclipse_keyword`."
    )

class MissingPropertyValueError(PropertyError):
    """Signal that a property contains missing grid values.

    This exception is raised when a property expected to be fully defined still
    includes missing values, such as NaN entries.

    Attributes
    ----------
    default_message : str
        Message template that identifies the property with missing values.
    """

    default_message = (
        "Property '{property_name}' contains missing values. "
        "Ensure all grid cells are assigned values. "
        "Use `fill_nan()` if appropriate."
    )

class ReservedPropertyNameError(PropertyError):
    """Signal that a reserved property name has been requested.

    This exception is raised when an operation attempts to create or register a
    property name that is part of a reserved set.

    Attributes
    ----------
    default_message : str
        Message template that includes the invalid name and reserved-name list.
    """

    default_message = (
        "'{property_name}' is a reserved property name and cannot be used. "
        "Reserved names are: {reserved_names}."
    )

    def __init__(self, message: str | None = None, **context: Any) -> None:
        """Initialize the error and normalize reserved-name display.

        If ``reserved_names`` is provided in the context mapping, its values are
        converted into a user-readable string before formatting the error
        message.

        Parameters
        ----------
        message : str or None, default=None
            Optional explicit error message. If omitted, ``default_message`` is
            used.
        **context : Any
            Formatting context used by the base error class. When
            ``reserved_names`` is present, it is transformed into a readable
            comma-separated representation.

        Returns
        -------
        None
            This constructor initializes the exception instance in place.
        """

        if "reserved_names" in context:
            context["reserved_names"] = _iterable_to_str(context["reserved_names"])

        super().__init__(
            message,
            **context
        )

class ExistingPropertyNameError(PropertyError):
    """Signal that a property name is already present.

    This exception is raised when an operation attempts to define a property
    using a name that already exists in the target property collection.

    Attributes
    ----------
    default_message : str
        Message template that contains the duplicate property name.
    """

    default_message = (
        "A property named '{property_name}' already exists. "
        "Choose a different name."
    )
