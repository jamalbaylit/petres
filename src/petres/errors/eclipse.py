from .base import ExportError, PetresError

class EclipseError(PetresError):
    default_message = "An error occurred related to Eclipse operations."

class GRDECLExportError(EclipseError, ExportError):
    default_message = "An error occurred during GRDECL export."

class GRDECLMissingValueError(GRDECLExportError):
    default_message = (
        "Failed to export keyword '{keyword}' because it contains NaN values. "
        "Ensure all values are defined."
    )