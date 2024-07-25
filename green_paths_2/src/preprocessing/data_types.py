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
    NoDataValue = "no_data_value"
    DataBuffer = "data_buffer"
    GoodExposure = "good_exposure"
    Rastercellresolution = "raster_cell_resolution"
    Originalcrs = "original_crs"
    MinDataValue = "min_data_value"
    MaxDataValue = "max_data_value"
    Columnsofinterest = "columns_of_interest"
    Saverasterfile = "save_raster_file"
    Origins = "origins"
    Destinations = "destinations"
    ODcrs = "od_crs"
    ODLonName = "od_lon_name"
    ODLatName = "od_lat_name"
    Sensitivity = "sensitivity"
    AllowMissingData = "allow_missing_data"
    ExposureParameters = "exposure_parameters"
    TransportMode = "transport_mode"
    KeepGeometry = "keep_geometry"
    CumulativeRanges = "cumulative_ranges"
    SaveOutputName = "save_output_name"
    DatasCoverageSafetyPercentage = "datas_coverage_safety_percentage"


class TravelModes(Enum):
    Walking: str = "walking"
    Cycling: str = "cycling"
