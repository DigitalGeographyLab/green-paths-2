""" Custom exceptions for the preprocessing module. """


class GreenPathsBaseError(Exception):
    """Base class for all custom exceptions in the application."""

    pass


class ConfigError(Exception):
    """Exception raised for errors in the configuration parsing."""

    def __init__(self, message="Error in configuration parsing."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"ConfigError: {self.message}"


class ConfigDataError(Exception):
    """Exception raised for invalid data_config.yaml datas configuration."""

    def __init__(self, message="Error in data configuration."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"ConfigDataError: {self.message}"


class PipeLineRuntimeError(Exception):
    """Exception raised for errors in the pipeline runtime."""

    def __init__(self, message="Error in pipeline runtime."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"PipeLineRuntimeError: {self.message}"


class SegmentValueStoreError(Exception):
    """Exception raised for errors in the segment value store."""

    def __init__(self, message="Error in segment value store."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"SegmentValueStoreError: {self.message}"


class SpatialOperationError(Exception):
    """Exception raised for errors in spatial operations."""

    def __init__(self, message="Error in spatial operations."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"SpatialOperationError: {self.message}"


class DataManagingError(Exception):
    """Exception raised for errors in data managing."""

    def __init__(self, message="Error in data managing."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"DataManagingError: {self.message}"


class OsmSegmenterError(Exception):
    """Exception raised for errors in the OSM segmenter."""

    def __init__(self, message="Error in OSM segmenter."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"OsmSegmenterError: {self.message}"


class R5pyError(Exception):
    """Exception raised for errors in the R5py routing."""

    def __init__(self, message="Error in R5py routing."):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"RoutingR5pyError: {self.message}"
