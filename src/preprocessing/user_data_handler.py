""" Data Source Handler Class """


from src.preprocessing.data_source import DataSource
from src.logging import setup_logger, LoggerColors


LOG = setup_logger(__name__, LoggerColors.GREEN.value)


class UserDataHandler:
    def __init__(self):
        self.data_sources = {}

    def get_data_sources(self):
        return self.data_sources

    def get_data_source_by_name(self, name):
        return self.data_sources.get(name)

    def set_data_sources(self, data_sources):
        self.data_sources = data_sources

    def add_data_source(self, data_source):
        self.data_sources[data_source.get("name")] = DataSource(**data_source)

    def populate_data_sources(self, data_sources: list[dict]):
        """Populate data sources from config dictionary."""
        for data_source in data_sources:
            self.add_data_source(data_source)


# roope todo -> poista nää
# [{

#'name': 'green_points',
# 'filepath': '/Users/hcroope/omat/GP2/data/greenery_points.gpkg',
# 'data_type': 'vector',
# 'layer_name': 'Helsinki_4326',
# 'original_crs': 3879},


# {'name': 'noise_helsinki', 'filepath': '/Users/hcroope/omat/GP2/data/Helsinki_noise_data_2022/Melualueet_2022_01_kadut_maant_LAeq7-22_NPM_20231116_123645.gml', 'data_type': 'vector', 'columns_of_interest': ['db_lo', 'db_hi', 'geometry'], 'original_crs': 3879}, {'name': 'test_data_source', 'filepath': 'not_a_file.gpkg', 'data_type': 'raster'}]
