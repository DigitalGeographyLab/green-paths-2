# TODO: add validator tests...

import os

import pytest
from ..src.preprocessing.user_config_parser import UserConfig


USER_CONFIG_PATH = "green_paths_2/user/config.yaml"


# test validator, eventhough it is run in all other pipeline tests automatically


# @pytest.mark.skip(reason="testing  so skipping")
def test_validator_valid_config(config_dir, valid_user_config):
    config_path = os.path.join(config_dir, valid_user_config)
    user_config = UserConfig(config_path).parse_config()

    assert user_config is not None
    assert user_config.data_source_names is not None
    assert user_config.errors == []


@pytest.mark.skip(reason="testing  so skipping")
def test_validator_invalid_config(config_dir, invalid_user_config):
    config_path = os.path.join(config_dir, invalid_user_config)
    user_config = UserConfig(config_path).parse_config()

    assert user_config is not None
    assert user_config.data_source_names is None
    assert user_config.errors != []

    # edittaa tota error yamlia!...

    # asserttaa mitä siel erroreis on ...
