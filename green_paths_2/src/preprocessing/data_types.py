""" Datatypes supported by the preprocessing module. """

from enum import Enum


class DataTypes(Enum):
    Vector = "vector"
    Raster = "raster"


class DataSourceModel(Enum):
    Name = "name"
    Filepath = "filepath"
    Datatype = "data_type"
    Datacolumn = "data_column"
    Rastercellresolution = "raster_cell_resolution"
    Originalcrs = "original_crs"
    Columnsofinterest = "columns_of_interest"
    Saverasterfile = "save_raster_file"
