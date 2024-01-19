""" Custom exceptions for the preprocessing module. """


class ConfigError(Exception):
    """Exception raised for errors in the configuration parsing."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ConfigDataError(Exception):
    """Exception raised for invalid data_config.yaml datas configuration."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
