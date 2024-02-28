""" Data Source Handler Class """

from green_paths_2.src.preprocessing.data_source import DataSource
from green_paths_2.src.logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.GREEN.value)


class UserDataHandler:
    def __init__(self):
        self.data_sources = {}

    def get_data_sources(self):
        return self.data_sources

    def get_data_source_by_name(self, name):
        return self.data_sources.get(name)

    def get_data_source_names(self):
        return list(self.data_sources.keys())

    def set_data_sources(self, data_sources):
        self.data_sources = data_sources

    def add_data_source(self, data_source):
        self.data_sources[data_source.get("name")] = DataSource(**data_source)

    def populate_data_sources(self, data_sources: list[dict]):
        """Populate data sources from config dictionary."""
        for data_source in data_sources:
            self.add_data_source(data_source)
