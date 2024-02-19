""" Datatypes supported by the preprocessing module. """
from enum import Enum


class DataTypes(Enum):
    Vector = "vector"
    Raster = "raster"


class DataSourceModel(Enum):
    Name = "name"
    Filepath = "filepath"
    Datatype = "data_type"
