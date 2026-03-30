class PetresError(Exception):
    default_message = "An unknown Petres error occurred."

    def __init__(self, message: str | None = None, **context):
        self.context = context

        if message is None:
            try:
                message = self.default_message.format(**context)
            except KeyError as e:
                missing = e.args[0]
                raise ValueError(
                    f"Missing context key '{missing}' for error message formatting "
                    f"in {self.__class__.__name__}"
                ) from None
        else:
            if context:
                message = message.format(**context)

        super().__init__(message)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.context})"


# ====================================
class VisualizationError(PetresError):
    default_message = "An error occurred related to visualization operations."

class ExportError(PetresError):
    default_message = "An error occurred related to data export operations."



