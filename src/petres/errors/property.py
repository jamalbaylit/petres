from ._utils import _iterable_to_str
from .base import PetresError


class PropertyError(PetresError):
    default_message = "An error occurred related to property operations."

# ====================================

class MissingEclipseKeywordError(PropertyError):
    """Raised when a property lacks an Eclipse keyword required for export."""

    default_message = (
        "Property '{property_name}' does not have an associated Eclipse keyword. "
        "Make sure to define the property with an `eclipse_keyword`."
    )

class MissingPropertyValueError(PropertyError):
    """Raised when a required property has missing values in the grid."""

    default_message = (
        "Property '{property_name}' contains missing values. "
        "Ensure all grid cells are assigned values. "
        "Use `fill_nan()` if appropriate."
    )

class ReservedPropertyNameError(PropertyError):
    """Raised when a property is defined with a reserved name."""

    default_message = (
        "'{property_name}' is a reserved property name and cannot be used. "
        "Reserved names are: {reserved_names}."
    )

    def __init__(self, message: str | None = None, **context):
        if "reserved_names" in context:
            context["reserved_names"] = _iterable_to_str(context["reserved_names"])

        super().__init__(
            message,
            **context
        )

class ExistingPropertyNameError(PropertyError):
    """Raised when a property with the same name already exists."""

    default_message = (
        "A property named '{property_name}' already exists. "
        "Choose a different name."
    )
