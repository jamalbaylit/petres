from __future__ import annotations

from typing import Any

"""Custom error hierarchy for the petres package."""


class PetresError(Exception):
    """Represent package-level exceptions with optional message formatting.

    Use this exception as the common base for package-specific failures. Message
    templates are formatted with keyword context values.

    Parameters
    ----------
    message : str | None, default=None
        Message template. If ``None``, use ``default_message``.
    **context : Any
        Keyword values used to format the selected template.

    Raises
    ------
    ValueError
        Raised when formatting requires a missing key from ``context``.
    """

    default_message: str = "An unknown Petres error occurred."

    def __init__(self, message: str | None = None, **context: Any) -> None:
        """Initialize the error and format the active message template."""
        self.context: dict[str, Any] = context

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
        """Return a developer-facing representation with class name and context.

        Returns
        -------
        str
            Representation containing the class name and stored context.
        """
        return f"{self.__class__.__name__}({self.context})"


# ====================================
class VisualizationError(PetresError):
    """Represent visualization-related errors.

    Use this specialization when rendering or display workflows encounter
    recoverable domain failures.
    """

    default_message: str = "An error occurred related to visualization operations."

class ExportError(PetresError):
    """Represent data-export-related errors.

    Use this specialization for failures during serialization or file export
    workflows.
    """

    default_message: str = "An error occurred related to data export operations."



