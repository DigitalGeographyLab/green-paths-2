""" Data Source Class / Model """

from typing import Any, Optional
from green_paths_2.src.logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.BLUE.value)


class DataSource:
    def __init__(
        self,
        name: str,
        filepath: str,
        good_exposure: bool,
        min_data_value: float,
        max_data_value: float,
        data_column: Optional[str] = None,
        data_buffer: Optional[int] = None,
        raster_cell_resolution: Optional[int] = None,
        data_type: Optional[str] = None,
        save_raster_file: Optional[bool] = None,
        original_crs: Optional[str] = None,
        columns_of_interest: Optional[list[str]] = None,
        custom_processing_function: Optional[str] = None,
        **source_specific_attributes: Any
    ):
        self.name = name
        self.filepath = filepath
        self.good_exposure = good_exposure
        self.min_data_value = min_data_value
        self.max_data_value = max_data_value
        self.data_type = data_type
        self.data_column = data_column
        self.data_buffer = data_buffer
        self.raster_cell_resolution = raster_cell_resolution
        self.original_crs = original_crs
        self.columns_of_interest = columns_of_interest
        self.save_raster_file = save_raster_file
        self.source_specific_attributes = source_specific_attributes
        self.custom_processing_function = custom_processing_function

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_filepath(self):
        return self.filepath

    def set_filepath(self, filepath: str):
        self.filepath = filepath

    def get_good_exposure(self):
        return self.good_exposure

    def set_good_exposure(self, good_exposure: bool):
        self.good_exposure = good_exposure

    def get_min_data_value(self):
        return self.min_data_value

    def set_min_data_value(self, min_data_value: float):
        self.min_data_value = min_data_value

    def get_max_data_value(self):
        return self.max_data_value

    def set_max_data_value(self, max_data_value: float):
        self.max_data_value = max_data_value

    def get_data_type(self):
        return self.data_type

    def set_data_type(self, data_type: str):
        self.data_type = data_type

    def get_original_crs(self):
        return self.original_crs

    def set_original_crs(self, original_crs: str):
        self.original_crs = original_crs

    def get_data_column(self):
        return self.data_column

    def set_data_column(self, data_column: str):
        self.data_column = data_column

    def get_data_buffer(self):
        return self.data_buffer

    def set_data_buffer(self, data_buffer: int):
        self.data_buffer = data_buffer

    def get_raster_cell_resolution(self):
        return self.raster_cell_resolution

    def set_raster_cell_resolution(self, raster_cell_resolution: int):
        self.raster_cell_resolution = raster_cell_resolution

    def get_columns_of_interest(self):
        return self.columns_of_interest

    def set_columns_of_interest(self, columns_of_interest: list[str]):
        self.columns_of_interest = columns_of_interest

    def get_custom_processing_function(self):
        return self.custom_processing_function

    def set_custom_processing_function(self, custom_processing_function: str):
        self.custom_processing_function = custom_processing_function

    def get_save_raster_file(self):
        return self.save_raster_file

    def get_data_specific_attributes(self):
        return self.source_specific_attributes

    def set_data_specific_attributes(self, source_specific_attributes: dict[str, Any]):
        self.source_specific_attributes = source_specific_attributes

    def get_data_specific_attribute(self, name: str):
        return self.source_specific_attributes.get(name)

    def set_data_specific_attribute(self, name: str, value: Any):
        self.source_specific_attributes[name] = value
