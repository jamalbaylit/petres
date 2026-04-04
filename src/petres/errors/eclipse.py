from __future__ import annotations

"""Eclipse/GRDECL-related error definitions."""

from typing import ClassVar

from .base import ExportError, PetresError


class EclipseError(PetresError):
    """Represent errors raised by Eclipse input and output operations.

    This exception specializes :class:`petres.errors.base.PetresError` for
    Eclipse-specific workflows and supports keyword interpolation through the
    inherited constructor.

    Parameters
    ----------
    message : str or None, default=None
        Error message template. If ``None``, :attr:`default_message` is used.
    **context : object
        Keyword values used to format the resolved message template.

    Notes
    -----
    Message formatting may raise :class:`ValueError` when a required template
    key is missing from ``context``.
    """

    default_message: ClassVar[str] = "An error occurred related to Eclipse operations."


class GRDECLExportError(EclipseError, ExportError):
    """Represent errors raised during GRDECL export operations.

    This exception captures generic failures that occur during GRDECL
    serialization and export routines.

    Parameters
    ----------
    message : str or None, default=None
        Error message template. If ``None``, :attr:`default_message` is used.
    **context : object
        Keyword values used to format the resolved message template.

    Notes
    -----
    Message formatting may raise :class:`ValueError` when a required template
    key is missing from ``context``.
    """

    default_message: ClassVar[str] = "An error occurred during GRDECL export."


class GRDECLMissingValueError(GRDECLExportError):
    """Represent errors raised when GRDECL export encounters missing values.

    This exception is intended for validation failures where exported keyword
    arrays still contain NaN values.

    Parameters
    ----------
    message : str or None, default=None
        Error message template. If ``None``, :attr:`default_message` is used.
    **context : object
        Keyword values used to format the resolved message template. The
        ``keyword`` value is expected by the default template.

    Notes
    -----
    The default template requires the ``keyword`` context key.
    """

    default_message: ClassVar[str] = (
        "Failed to export keyword '{keyword}' because it contains NaN values. "
        "Ensure all values are defined."
    )