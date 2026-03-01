

# class BoundaryModel:
#     def __init__(
#         self, 
#         source: Union[pd.DataFrame, str],
#         col_x: str,
#         col_y: str
#     ):
#         self.col_x = col_x
#         self.col_y = col_y
#         self.df = source if isinstance(source, pd.DataFrame) else pd.read_excel(source)
#         self.df = self._process(self.df)
#         self.x = self.df[self.col_x].to_numpy(dtype=np.float64)
#         self.y = self.df[self.col_y].to_numpy(dtype=np.float64)
    
#     def _process(self, df: pd.DataFrame) -> pd.DataFrame:
#         df = df.loc[:, [self.col_x, self.col_y]].copy()
#         df = Helper.remove_empty_rows(df)
#         df[self.col_x] = pd.to_numeric(df[self.col_x], errors='coerce')
#         df[self.col_y] = pd.to_numeric(df[self.col_y], errors='coerce')
#         return df
        