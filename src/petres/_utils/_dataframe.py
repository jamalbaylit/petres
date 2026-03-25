from collections.abc import Iterable
import pandas as pd

class DataFrameUtils:
    # == Column Validation Methods ==
    @staticmethod
    def require_columns(df: pd.DataFrame, required: Iterable[str]) -> None:
        missing = set(required) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {sorted(missing)}")
        
    @staticmethod
    def has_columns(df: pd.DataFrame, required: Iterable[str]) -> bool:
        return set(required).issubset(df.columns)
    
    @staticmethod
    def missing_columns(df: pd.DataFrame, required: Iterable[str]) -> list[str]:
        return sorted(set(required) - set(df.columns))
    
    