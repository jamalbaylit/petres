from ._utils import _iterable_to_str
from .base import PetresError

class GridError(PetresError):
    default_message = "An error occurred related to grid operations."

# ====================================

class UnsupportedGridAttributeError(GridError):
    """Raised when an unsupported grid attribute is accessed."""
    

    default_message = (
        "Unsupported grid attribute '{attribute_name}'. "
        "Supported attributes are: {supported_names}."
    )

    def __init__(self, message: str | None = None, **context):
        if "supported_names" in context:
            context["supported_names"] = _iterable_to_str(context["supported_names"])

        super().__init__(
            message,
            **context
        )
