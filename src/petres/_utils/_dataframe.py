"""Utilities for validating pandas DataFrame schemas."""

from collections.abc import Iterable
import pandas as pd

class DataFrameUtils:
    """Static helpers for checking required DataFrame columns."""

    # == Column Validation Methods ==
    @staticmethod
    def require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
        """Validate that all required columns exist, raising if any are missing.

        Parameters
        ----------
        df : pandas.DataFrame
            Input DataFrame to validate.
        required : Iterable[str]
            Column names that must be present.

        Raises
        ------
        ValueError
            If one or more required columns are absent.
        """
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        
    @staticmethod
    def has_columns(df: pd.DataFrame, required: Iterable[str]) -> bool:
        """Return True if all required columns are present."""
        return set(required).issubset(df.columns)
    
    @staticmethod
    def missing_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
        """List missing required columns sorted alphabetically."""
        return sorted(set(required) - set(df.columns))
    
    