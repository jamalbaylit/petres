# from dataclasses import dataclass
# from typing import Optional, Union
# from unicodedata import numeric
# from matplotlib.pyplot import fill
# from numpy.typing import NDArray
# import pandas as pd
# import numpy as np

# @dataclass
# class WellInstance:
#     """Well instance data with name and coordinates."""
#     name: str
#     x: float
#     y: float
#     top: float
#     bottom: float

# @dataclass
# class LayerInstance:
#     name: str
#     tops: NDArray[np.float64]      # 1D float array
#     bottoms: NDArray[np.float64]   # 1D float array
#     wells: list[WellInstance]

#     def __post_init__(self):
#         # Make sure top and bottom lists have the same length as well list
#         if not (len(self.tops) == len(self.bottoms) == len(self.wells)):
#             raise ValueError(
#                 f"Invalid LayerInstance for '{self.name}': top, bottom, and well lists must have the same length. However, got {len(self.tops)}, {len(self.bottoms)}, {len(self.wells)}."
#             )
#         # assert all tops are less than bottoms
#         for top, bottom in zip(self.tops, self.bottoms):
#             if top >= bottom:
#                 raise ValueError(
#                     f"Invalid LayerInstance for '{self.name}': each top ({top}) must be lower than bottom ({bottom})."
#                 )

#     def get_well(self, well_name: str) -> Optional[WellInstance]:
#         for i, well in enumerate(self.wells):
#             if well.name == well_name:
#                 return well, self.tops[i], self.bottoms[i]
#         return None

# @dataclass
# class ZoneInstance:
#     name: str
#     layers: list[LayerInstance]
#     top: float = None
#     bottom: float = None

#     def __post_init__(self):
#         self.top = min(min(layer.tops) for layer in self.layers)
#         self.bottom = max(max(layer.bottoms) for layer in self.layers)

        
# class Helper:
#     @staticmethod
#     def print_header(title: str, width: int = 60):
#         print(f"|{'=' * width}|")
#         print(f"|{title.upper():^{width}}|")
#         print(f"|{'=' * width}|")
    
#     @staticmethod
#     def remove_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
#         rows_with_nan = df.isna().any(axis=1)
#         if rows_with_nan.any():
#             print(
#                 "⚠️  The following rows have missing data and will be dropped:\n"
#                 f"{df.loc[rows_with_nan]}"
#             )
#         return df.loc[~rows_with_nan]
    

# class FieldData:
#     def __init__(
#         self,
#         zone_source: Union[pd.DataFrame, str],
#         zone_col_zone: str,
#         zone_col_layer: str, 
#         zone_col_well: str,
#         zone_col_top: str,
#         zone_col_bottom: str,
#         well_source: Union[pd.DataFrame, str],
#         well_col_well: str,
#         well_col_x: str,
#         well_col_y: str,
#     ):
#         self.zone_col_zone = zone_col_zone
#         self.zone_col_layer = zone_col_layer
#         self.zone_col_well = zone_col_well
#         self.zone_col_top = zone_col_top
#         self.zone_col_bottom = zone_col_bottom
#         self.well_col_well = well_col_well
#         self.well_col_x = well_col_x
#         self.well_col_y = well_col_y
#         self.zone_df = zone_source if isinstance(zone_source, pd.DataFrame) else pd.read_excel(zone_source)
#         self.well_df = well_source if isinstance(well_source, pd.DataFrame) else pd.read_excel(well_source)
#         self.zone_df = self._process_zone_df(self.zone_df)
#         self.well_df = self._process_well_df(self.well_df)
#         self.df = self._create_df(self.zone_df, self.well_df)
#         self.wells = self._create_wells(self.df)
#         self.layers = self._create_layers(self.df)
#         self.zones = self._create_zones(self.df)
#         self.layers_top_matrix, self.layers_bottom_matrix, self.layers_center_matrix, self.layers_thickness_matrix = self._build_top_bottom_matrices()
#         self.well_x_coords, self.well_y_coords, self.well_distance_matrix = self._build_well_params()


#     def _build_well_params(self):
#         self.well_x_coords = self.well_df[self.well_col_x].to_numpy(dtype=np.float64)
#         self.well_y_coords = self.well_df[self.well_col_y].to_numpy(dtype=np.float64)
#         def _well_distance_matrix():
#             x = self.well_x_coords
#             y = self.well_y_coords
#             dx = x[:, None] - x[None, :]
#             dy = y[:, None] - y[None, :]
#             D = np.sqrt(dx**2 + dy**2)
#             D[D == 0] = 1e-12
#             return D
#         self.well_distance_matrix = _well_distance_matrix()
        
#         return self.well_x_coords, self.well_y_coords, self.well_distance_matrix
    
#     def add_zero_zones(self, power: float=2) -> None:
#         self.layers_center_matrix = self._interpolate_center_matrix(power=power)
#         nan_mask = np.isnan(self.layers_top_matrix)
#         self.layers_top_matrix[nan_mask] = self.layers_center_matrix[nan_mask]
#         self.layers_bottom_matrix[nan_mask] = self.layers_center_matrix[nan_mask]
#         self.layers_thickness_matrix = self.layers_bottom_matrix - self.layers_top_matrix

#         if np.isnan(self.layers_top_matrix).any() or np.isnan(self.layers_bottom_matrix).any():
#             nan_layer_idx = np.where(np.isnan(self.layers_top_matrix).any(axis=1))[0]
#             nan_layers = np.array(self.layer_names())[nan_layer_idx].tolist()
#             raise ValueError(
#                 f"❌ Some zone tops/bottoms could not be interpolated. "
#                 f"Zones: {nan_layers}"
#             )
        

#         # fill self.layers_thickness_matrix nan values with zeros
#         # interpolated_thicknesses = self.layers_thickness_matrix.copy()
#         # nan_mask = np.isnan(interpolated_thicknesses)
#         # interpolated_thicknesses[nan_mask] = 0.0


#         # interpolated_centers_df = pd.DataFrame(
#         #     interpolated_centers,
#         #     index=self.layer_names(),
#         #     columns=self.well_names()
#         # )
#         # interpolated_centers_df.to_excel(f'interpolated_centers.xlsx')
#         # interpolated_thicknesses_df = pd.DataFrame(
#         #     interpolated_thicknesses,
#         #     index=self.layer_names(),
#         #     columns=self.well_names()
#         # )
#         # interpolated_thicknesses_df.to_excel(f'interpolated_thicknesses.xlsx')


#     def _interpolate_matrix_idw(self, matrix: NDArray[np.float64], power: float=2) -> NDArray[np.float64]:
#         D = self.well_distance_matrix
#         filled = matrix.copy()

#         for i in range(matrix.shape[0]):  # unavoidable, cheap
#             z = matrix[i]
#             known = ~np.isnan(z)
#             missing = np.isnan(z)

#             if missing.sum() == 0 or known.sum() < 2:
#                 continue

#             W = 1.0 / D[np.ix_(known, missing)] ** power
#             z_known = z[known]

#             filled[i, missing] = (W * z_known[:, None]).sum(axis=0) / W.sum(axis=0)

#         return filled
    
#     def _interpolate_center_matrix(self, power: float=2) -> NDArray[np.float64]:
#         matrix = self.layers_center_matrix.copy()
#         filled = self._interpolate_matrix_idw(matrix, power=power)

#         if np.isnan(filled).any():
#             nan_layer_idx = np.where(np.isnan(filled).any(axis=1))[0]
#             nan_layers = np.array(self.layer_names())[nan_layer_idx].tolist()

#             print(
#                 f"⚠️  Some zone centers could not be interpolated. "
#                 f"Zones: {nan_layers}"
#             )

#             for i in range(filled.shape[0]):
#                 row = filled[i]
#                 nan_mask = np.isnan(row)

#                 if nan_mask.any():
#                     valid = row[~nan_mask]

#                     if valid.size == 0:
#                         print(f"⚠️  Layer '{self.layer_names()[i]}' has no valid centers at all.")
#                         continue

#                     # Copy first valid value (or use np.mean(valid))
#                     row[nan_mask] = valid[0]



#         return filled

#     def _build_top_bottom_matrices(self):
#         """
#         Build top and bottom depth matrices.

#         Returns
#         -------
#         top : np.ndarray
#             Shape (n_layers, n_wells)
#         bottom : np.ndarray
#             Shape (n_layers, n_wells)
#         layers : list[str]
#             Row labels
#         wells : list[str]
#             Column labels
#         """

#         # Stable ordering
#         layers = self.layer_names()
#         wells = self.well_names()

#         n_layers = len(layers)
#         n_wells = len(wells)

#         layer_idx = {name: i for i, name in enumerate(layers)}
#         well_idx = {name: j for j, name in enumerate(wells)}

#         top = np.full((n_layers, n_wells), np.nan, dtype=float)
#         bottom = np.full((n_layers, n_wells), np.nan, dtype=float)

#         for row in self.df.itertuples(index=False):
#             i = layer_idx[getattr(row, self.zone_col_layer)]
#             j = well_idx[getattr(row, self.zone_col_well)]

#             top[i, j] = getattr(row, self.zone_col_top)
#             bottom[i, j] = getattr(row, self.zone_col_bottom)

#         # top_df = pd.DataFrame(
#         #     top,
#         #     index=layers,
#         #     columns=wells
#         # )
#         center = 0.5 * (top + bottom)
#         thickness = bottom - top
#         return top, bottom, center, thickness



#     def merge_layers(
#         self,
#         new_layer_name: str,
#         layers_to_merge: list[str],
#     ) -> None:
#         # Create a new dataframe with merged layer data
#         new_zone_rows = []
        
#         for well_name, well_group in self.zone_df.groupby(self.zone_col_well):
#             # Get rows for layers to merge
#             merge_mask = well_group[self.zone_col_layer].isin(layers_to_merge)
#             layers_data = well_group[merge_mask]
            
#             if not layers_data.empty:
#                 # Calculate weighted center and total thickness
#                 tops = layers_data[self.zone_col_top].values
#                 bottoms = layers_data[self.zone_col_bottom].values
                
#                 # Check for layers between the ones being merged
#                 merge_top = np.min(tops)
#                 merge_bottom = np.max(bottoms)
                
#                 other_layers = well_group[~merge_mask]
#                 if not other_layers.empty:
#                     # Vectorized check: any layer that overlaps with merge range
#                     overlapping = (
#                         ((other_layers[self.zone_col_top] > merge_top) & (other_layers[self.zone_col_top] < merge_bottom)) |
#                         ((other_layers[self.zone_col_bottom] > merge_top) & (other_layers[self.zone_col_bottom] < merge_bottom)) |
#                         ((other_layers[self.zone_col_top] <= merge_top) & (other_layers[self.zone_col_bottom] >= merge_bottom))
#                     )
                    
#                     if overlapping.any():
#                         conflicting = other_layers[overlapping].iloc[0]
#                         raise ValueError(
#                             f"Cannot merge layers {layers_to_merge} for well '{well_name}': "
#                             f"Layer '{conflicting[self.zone_col_layer]}' "
#                             f"(top={conflicting[self.zone_col_top]:.2f}, bottom={conflicting[self.zone_col_bottom]:.2f}) "
#                             f"is between the layers being merged (top={merge_top:.2f}, bottom={merge_bottom:.2f})."
#                         )
                
#                 centers = 0.5 * (tops + bottoms)
#                 lengths = bottoms - tops
#                 total_thickness = np.sum(lengths)
#                 weighted_center = np.sum(centers * lengths) / np.sum(lengths)
                
#                 # New top and bottom based on weighted center and total thickness
#                 new_top = weighted_center - total_thickness / 2
#                 new_bottom = weighted_center + total_thickness / 2
                
#                 # Create new row for merged layer
#                 new_row = layers_data.iloc[0].copy()
#                 new_row[self.zone_col_layer] = new_layer_name
#                 new_row[self.zone_col_top] = new_top
#                 new_row[self.zone_col_bottom] = new_bottom
#                 new_zone_rows.append(new_row)
        
#         # Update dataframe: remove old layers and add new merged layer
#         if new_zone_rows:
#             # update zone_df
#             new_zone_df = pd.DataFrame(new_zone_rows)
#             # check if layer and well combinations in new_zone_df already exists in self.zone_df and raise error if yes, and suggest to merge those layers also
#             duplicates = (
#                 self.zone_df[[self.zone_col_layer, self.zone_col_well]]
#                 .merge(
#                     new_zone_df[[self.zone_col_layer, self.zone_col_well]],
#                     on=[self.zone_col_layer, self.zone_col_well],
#                     how="inner"
#                 )
#             )

#             if not duplicates.empty:
#                 conflicting_layers = (
#                     duplicates[self.zone_col_layer]
#                     .drop_duplicates()
#                     .sort_values()
#                     .tolist()
#                 )

#                 print("❌  Cannot merge layers due to existing layer–well combinations:")
#                 print(
#                     duplicates
#                     .sort_values([self.zone_col_layer, self.zone_col_well])
#                     .to_string(index=False)
#                 )

#                 print("\n💡 Suggested layers to also include in `layers_to_merge`:")
#                 print(conflicting_layers)

#                 raise ValueError(
#                     "Some layer–well combinations already exist in the zone data. "
#                     "Include the suggested layers in `layers_to_merge` and retry."
#                 )

#             new_zone_df = pd.concat([
#                 self.zone_df[~self.zone_df[self.zone_col_layer].isin(layers_to_merge)],
#                 new_zone_df    
#             ], ignore_index=True)

#             self.__init__(
#                 zone_source=new_zone_df,
#                 zone_col_zone=self.zone_col_zone,
#                 zone_col_layer=self.zone_col_layer,
#                 zone_col_well=self.zone_col_well,
#                 zone_col_top=self.zone_col_top,
#                 zone_col_bottom=self.zone_col_bottom,
#                 well_source=self.well_df,
#                 well_col_well=self.well_col_well,
#                 well_col_x=self.well_col_x,
#                 well_col_y=self.well_col_y,
#             )
#         else:
#             raise ValueError(
#                 f"No layers to merge found for new layer '{new_layer_name}'."
#             )

        
                    

        
#     def zone_info(self) -> None:
#         Helper.print_header("Zone Information")
#         for zone_name, zone in self.zones.items():
#             print(f"Zone: {zone_name}")
#             for layer in zone.layers:
#                 print(f"  - Layer: {layer.name}, Number of wells: {len(layer.wells)}")

#     def get_well(self, well_name: str) -> WellInstance:
#         return self.wells[well_name]

#     def find_well(self, well_name: str) -> Optional[WellInstance]:
#         return self.wells.get(well_name)
    
#     def get_layer(self, layer_name: str) -> LayerInstance:
#         return self.layers[layer_name]

#     def find_layer(self, layer_name: str) -> Optional[LayerInstance]:
#         return self.layers.get(layer_name)

#     def get_zone(self, zone_name: str) -> ZoneInstance:
#         return self.zones[zone_name]

#     def find_zone(self, zone_name: str) -> Optional[ZoneInstance]:
#         return self.zones.get(zone_name)

#     def zone_names(self) -> list[str]:
#         return self.df[self.zone_col_zone].unique().tolist()

#     def layer_names(self) -> list[str]:
#         return self.df[self.zone_col_layer].unique().tolist()
    
#     def well_names(self) -> list[str]:
#         return self.well_df[self.well_col_well].unique().tolist()
    
#     def _process_zone_df(self, df: pd.DataFrame) -> pd.DataFrame:
#         df = df.loc[:, [self.zone_col_zone, self.zone_col_layer, self.zone_col_well, self.zone_col_top, self.zone_col_bottom]].copy()
#         dubs = df[df.duplicated(subset=[self.zone_col_layer, self.zone_col_well], keep=False)]
#         if not dubs.empty:
#             print("❌  Duplicate layer–well combinations found in zone data:")
#             print(
#                 dubs
#                 .sort_values([self.zone_col_layer, self.zone_col_well])
#                 .to_string(index=False)
#             )
#         return Helper.remove_empty_rows(df)
        
#     def _process_well_df(self, df: pd.DataFrame) -> pd.DataFrame:
#         df = df.loc[:, [self.well_col_well, self.well_col_x, self.well_col_y]].copy()
        
#         df[self.well_col_well] = df[self.well_col_well].astype(str)
#         dubs = df[df.duplicated(subset=[self.well_col_well], keep=False)]
#         if not dubs.empty:
#             print("❌  Duplicate well names found in well data:")
#             print(
#                 dubs
#                 .sort_values(self.well_col_well)
#                 .to_string(index=False)
#             )
#         return Helper.remove_empty_rows(df)
    
#     def _create_wells(self, df: pd.DataFrame) -> dict[str, WellInstance]:
#         """
#         Docstring for create_wells
        
#         :param self: Description
#         :param df: Description
#         :type df: pd.DataFrame
#         :return: Description
#         :rtype: dict[str, WellInstance]
#         """
#         wells = { 
#             well_name: WellInstance(
#                 name=well_name,
#                 x=group[self.well_col_x].iloc[0],
#                 y=group[self.well_col_y].iloc[0],
#                 top=group[self.zone_col_top].min(),
#                 bottom=group[self.zone_col_bottom].max()
#             ) for well_name, group in df.groupby(self.zone_col_well)
#         }
#         return wells

#     def _create_layers(self, df: pd.DataFrame) -> dict[str, LayerInstance]:
#         """
#         Docstring for create_layers
        
#         :param self: Description
#         :param df: Description
#         :type df: pd.DataFrame
#         :return: Description
#         :rtype: dict[str, LayerInstance]
#         """ 
#         layers = {
#             layer_name: LayerInstance(
#                 name=layer_name,
#                 tops=group[self.zone_col_top].to_numpy(dtype=np.float64),
#                 bottoms=group[self.zone_col_bottom].to_numpy(dtype=np.float64),
#                 wells=[self.wells[row[self.zone_col_well]] for _, row in group.iterrows()]
#             )
#             for layer_name, group in self.df.groupby(self.zone_col_layer) 
#         }

#         return layers
    
#     def _create_zones(self, df: pd.DataFrame) -> dict[str, ZoneInstance]:
#         """
#         Docstring for create_zones
        
#         :param self: Description
#         :param df: Description
#         :type df: pd.DataFrame
#         :return: Description
#         :rtype: dict[str, ZoneInstance]
#         """ 

#         zones = {
#             zone_name: ZoneInstance(
#                 name=zone_name,
#                 layers=[
#                     self.layers[layer_name] for layer_name in group[self.zone_col_layer].unique()
#                 ]
#             ) for zone_name, group in self.df.groupby(self.zone_col_zone)
#         }
#         return zones
    
    
    

       

#     def _create_df(self, zone_df: pd.DataFrame, well_df: pd.DataFrame) -> pd.DataFrame:
#         """Process the dataframe to ensure data integrity."""
#         df = zone_df.merge(
#             well_df[[self.well_col_well, self.well_col_x, self.well_col_y]],
#             left_on=self.zone_col_well,
#             right_on=self.well_col_well,
#             how='left'
#         )
#         missing_wells = df[df[self.well_col_x].isna()][self.zone_col_well].unique().tolist()
#         if missing_wells:
#             print(f"⚠️  The following wells are missing coordinates in wells data which are existing in zones: {missing_wells}")
#         df = df.dropna(subset=[self.well_col_x, self.well_col_y])
        

#         # Check for duplicate layer–well combinations
#         dups = df[df.duplicated(
#             subset=[self.zone_col_layer, self.zone_col_well],
#             keep=False
#         )]
        
#         if not dups.empty:
#             print("\n❌ Duplicate layer–well combinations found:")
#             print(
#                 dups
#                 .sort_values([self.zone_col_layer, self.zone_col_well])
#                 .to_string(index=False)
#             )

#         assert dups.empty, "Zones dataframe contains duplicate layer–well combinations."



#         layer_zone_counts = (
#             df
#             .groupby(self.zone_col_layer)[self.zone_col_zone]
#             .nunique()
#         )
#         invalid_layers = layer_zone_counts[layer_zone_counts > 1]
#         if not invalid_layers.empty:
#             print(
#                 "⚠️  Some layers belong to more than one zone:\n"
#                 + invalid_layers.to_string()
#             )
#         assert invalid_layers.empty, "Some layers belong to more than one zone."



#         # at the end of the day keep the wells in self.well_df existing in zones only and report removed ones
#         valid_wells = df[self.zone_col_well].unique()
#         removed_wells = well_df[~well_df[self.well_col_well].isin(valid_wells)]
#         if not removed_wells.empty:
#             print(
#                 "⚠️  The following wells are not used in any zone and will be removed from well data:\n"
#                 + removed_wells.to_string(index=False)
#             )  
#         self.well_df = self.well_df[self.well_df[self.well_col_well].isin(valid_wells)]
#         return df
    




