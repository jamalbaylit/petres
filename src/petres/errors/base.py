"""Custom error hierarchy for the petres package."""


class PetresError(Exception):
    """Represent a base exception with optional context-driven formatting.

    This exception provides a consistent error base for the package and supports
    formatting either a provided message template or the class-level
    ``default_message`` using keyword context values.
    """

    default_message: str = "An unknown Petres error occurred."

    def __init__(self, message: str | None = None, **context: object) -> None:
        """Initialize the exception with optional template formatting context.

        If ``message`` is not provided, the class-level ``default_message`` is
        formatted with ``context``. When ``message`` is provided, it is used as
        a template and formatted with ``context`` only if context values exist.

        Parameters
        ----------
        message : str or None, default=None
            Error message template. If ``None``, ``default_message`` is used.
        **context : object
            Keyword values used to format the selected message template.

        Returns
        -------
        None
            This method initializes the exception instance.

        Raises
        ------
        ValueError
            Raised when formatting requires a missing key from ``context``.
        """
        self.context: dict[str, object] = context

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

    def __repr__(self) -> str:
        """Return a developer-focused representation of the error.

        Parameters
        ----------
        None

        Returns
        -------
        str
            Representation containing the class name and stored context.
        """
        return f"{self.__class__.__name__}({self.context})"


# ====================================
class VisualizationError(PetresError):
    """Represent errors raised by visualization-related operations.

    This specialization is used when rendering or display workflows encounter
    recoverable domain-specific failures.
    """

    default_message: str = "An error occurred related to visualization operations."

class ExportError(PetresError):
    """Represent errors raised while exporting data to external formats.

    This specialization captures failures during serialization or file export
    workflows.
    """

    default_message: str = "An error occurred related to data export operations."



