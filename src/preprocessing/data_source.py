""" Data Source Class / Model """

from typing import Any, Optional
from src.logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.BLUE.value)


class DataSource:
    def __init__(
        self,
        name: str,
        filepath: str,
        data_type: str,
        data_column: str,
        original_crs: Optional[str] = None,
        columns_of_interest: Optional[list[str]] = None,
        **source_specific_attributes: Any
    ):
        self.name = name
        self.filepath = filepath
        self.data_type = data_type
        self.data_column = data_column
        self.original_crs = original_crs
        self.columns_of_interest = columns_of_interest
        self.source_specific_attributes = source_specific_attributes

    def get_name(self):
        return self.name

    def set_name(self, name: str):
        self.name = name

    def get_filepath(self):
        return self.filepath

    def set_filepath(self, filepath: str):
        self.filepath = filepath

    def get_data_type(self):
        return self.data_type

    def set_data_type(self, data_type: str):
        self.data_type = data_type

    def get_original_crs(self):
        return self.original_crs

    def set_original_crs(self, original_crs: str):
        self.original_crs = original_crs

    def get_columns_of_interest(self):
        return self.columns_of_interest

    def set_columns_of_interest(self, columns_of_interest: list[str]):
        self.columns_of_interest = columns_of_interest

    def get_data_specific_attributes(self):
        return self.source_specific_attributes

    def set_data_specific_attributes(self, source_specific_attributes: dict[str, Any]):
        self.source_specific_attributes = source_specific_attributes

    def get_data_specific_attribute(self, name: str):
        return self.source_specific_attributes.get(name)

    def set_data_specific_attribute(self, name: str, value: Any):
        self.source_specific_attributes[name] = value
