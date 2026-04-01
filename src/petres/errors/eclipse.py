"""Eclipse/GRDECL-related error definitions."""

from __future__ import annotations

from typing import ClassVar

from .base import ExportError, PetresError


class EclipseError(PetresError):
    """Base error for Eclipse input and output operations.

    This exception specializes :class:`petres.errors.base.PetresError` for
    Eclipse-specific workflows. Message formatting follows the inherited
    constructor behavior and supports keyword interpolation.

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
    """Base error for GRDECL export operations.

    This exception is raised for generic failures during GRDECL serialization
    and export routines.

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
    """Raise when GRDECL export encounters missing values for a keyword.

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