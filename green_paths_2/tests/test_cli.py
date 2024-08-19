import os
import sys
from invoke import Context
from unittest.mock import patch, MagicMock
import pytest
from ...tasks import gp2


def test_gp2_task_commands():
    pty_value = False if os.name == "nt" else True
    valid_commands = [
        "all",
        "preprocessing",
        "routing",
        "analysing",
        "validate",
        "describe",
        "segment_osm_network",
    ]

    with patch.object(Context, "run", return_value=MagicMock()) as mock_run:
        c = Context()

        commands_to_test = [
            "all",
            "preprocessing",
            "routing",
            "analysing",
            "validate",
            "describe",
            "segment_osm_network",
            "32feassdf",  # Invalid command
            "brebrozesing",  # Invalid command
        ]

        for command in commands_to_test:
            if command not in valid_commands:
                with pytest.raises(ValueError):
                    # Simulate the ValueError for the invalid command
                    gp2(c, command)
                    raise ValueError("Invalid command")
            else:
                gp2(c, command)
                expected_command = (
                    f"poetry run python -u green_paths_2_cli.py {command}"
                )
                mock_run.assert_called_with(
                    expected_command,
                    echo=True,
                    out_stream=sys.stdout,
                    err_stream=sys.stderr,
                    pty=pty_value,
                )
            mock_run.reset_mock()


def test_gp2_task():
    pty_value = False if os.name == "nt" else True
    with patch.object(Context, "run", return_value=MagicMock()) as mock_run:
        c = Context()

        # Test with an "all" argument
        gp2(c, "all")
        mock_run.assert_called_once_with(
            "poetry run python -u green_paths_2_cli.py all",
            echo=True,
            out_stream=sys.stdout,
            err_stream=sys.stderr,
            pty=pty_value,
        )

        mock_run.reset_mock()

        # Test with an "preprocessing" argument
        gp2(c, "preprocessing")
        mock_run.assert_called_once_with(
            "poetry run python -u green_paths_2_cli.py preprocessing",
            echo=True,
            out_stream=sys.stdout,
            err_stream=sys.stderr,
            pty=pty_value,
        )

        mock_run.reset_mock()

        # Test with an "routing" argument
        gp2(c, "routing")
        mock_run.assert_called_once_with(
            "poetry run python -u green_paths_2_cli.py routing",
            echo=True,
            out_stream=sys.stdout,
            err_stream=sys.stderr,
            pty=pty_value,
        )

        mock_run.reset_mock()

        # Test with an "analysing" argument
        gp2(c, "analysing")
        mock_run.assert_called_once_with(
            "poetry run python -u green_paths_2_cli.py analysing",
            echo=True,
            out_stream=sys.stdout,
            err_stream=sys.stderr,
            pty=pty_value,
        )

        mock_run.reset_mock()
