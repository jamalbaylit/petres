class PetresError(Exception):
    default_message = "An unknown Petres error occurred."

    def __init__(self, message: str | None = None, **context):
        self.context = context
        self.__dict__.update(context)

        if message is None:
            try:
                message = self.default_message.format(**context)
            except KeyError:
                message = self.default_message

        super().__init__(message)


# ====================================

class GridError(PetresError):
    default_message = "An error occurred related to grid operations."


class PropertyError(PetresError):
    default_message = "An error occurred related to property operations."


class HorizonError(PetresError):
    default_message = "An error occurred related to horizon operations."


class ZoneError(PetresError):
    default_message = "An error occurred related to zone operations."


class InterpolationError(PetresError):
    default_message = "An error occurred related to interpolation operations."

# ====================================
class MissingEclipseKeywordError(PropertyError):
    """Raised when a property lacks an Eclipse keyword required for export."""

    default_message = (
        "Property '{property_name}' does not have an associated Eclipse keyword. "
        "Make sure to define the property with an `eclipse_keyword`."
    )