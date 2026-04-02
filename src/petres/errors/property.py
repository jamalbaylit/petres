from __future__ import annotations

"""Define property-related exception types."""

from typing import Any

from ._utils import _iterable_to_str
from .base import PetresError


class PropertyError(PetresError):
    """Represent the base exception for property-modeling failures."""

    default_message: str = "An error occurred related to property operations."

# ====================================

class MissingEclipseKeywordError(PropertyError):
    """Indicate that a property is missing an Eclipse export keyword."""

    default_message: str = (
        "Property '{property_name}' does not have an associated Eclipse keyword. "
        "Make sure to define the property with an `eclipse_keyword`."
    )

class MissingPropertyValueError(PropertyError):
    """Indicate that a property contains missing grid values."""

    default_message: str = (
        "Property '{property_name}' contains missing values. "
        "Ensure all grid cells are assigned values. "
        "Use `fill_nan()` if appropriate."
    )

class ReservedPropertyNameError(PropertyError):
    """Indicate that a reserved property name was requested.

    Parameters
    ----------
    message : str | None, default=None
        Explicit error message template. If not provided, ``default_message``
        is used.
    **context : Any
        Context used to format the error message. If ``reserved_names`` is
        provided, it must be iterable and is rendered to a human-readable
        string.
    """

    default_message: str = (
        "'{property_name}' is a reserved property name and cannot be used. "
        "Reserved names are: {reserved_names}."
    )

    def __init__(self, message: str | None = None, **context: Any) -> None:
        """Initialize the error and normalize reserved-name formatting."""

        if "reserved_names" in context:
            context["reserved_names"] = _iterable_to_str(context["reserved_names"])

        super().__init__(
            message,
            **context
        )

class ExistingPropertyNameError(PropertyError):
    """Indicate that a property name already exists."""

    default_message: str = (
        "A property named '{property_name}' already exists. "
        "Choose a different name."
    )
