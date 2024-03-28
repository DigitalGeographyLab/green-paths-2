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
    DataBuffer = "data_buffer"
    GoodExposure = "good_exposure"
    Rastercellresolution = "raster_cell_resolution"
    Originalcrs = "original_crs"
    MinDataValue = "min_data_value"
    MaxDataValue = "max_data_value"
    Columnsofinterest = "columns_of_interest"
    Saverasterfile = "save_raster_file"
    Computer = "computer"
    Origins_destinations = "origins_destinations"
    Sensitivity = "sensitivity"
    AllowMissingData = "allow_missing_data"
    ExposureParameters = "exposure_parameters"
    TransportMode = "transport_mode"


# TODO: maybe rename this file?


class RoutingComputers(Enum):
    Matrix: str = "matrix"
    Detailed: str = "detailed"


# TODO -> should there be CAR here?
class TravelModes(Enum):
    Walking: str = "walking"
    Cycling: str = "cycling"
