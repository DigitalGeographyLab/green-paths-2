"""Cli user interface for Green paths 2."""

import sys
import os

# Ensuring the root of the project is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import argparse

from green_paths_2.src.pipeline_controller import handle_pipelines
from green_paths_2.src.cache_cleaner import clear_db
from green_paths_2.src.config_validator import validate_user_config
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.preprocessing.data_descriptor import (
    DataDescriptor,
)

from green_paths_2.src.preprocessing.osm_segmenter import (
    segment_or_use_cache_osm_network,
)
from green_paths_2.src.preprocessing.user_config_parser import UserConfig
from green_paths_2.src.routing.main import routing_pipeline

LOG = setup_logger(__name__, LoggerColors.BLUE.value)

# NOTE: this is a temporary solution to ignore FutureWarnings from geopandas from pyrosm
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def main():
    LOG.info(
        "\n\n  \033[95m Greetings traveller! Welcome to Green paths 2 cli user interface. Please provide an action. \n\n (Use 'action' --help' for information on each actions arguments.) \033[0m"
    )
    parser = argparse.ArgumentParser(
        description="\033[92m Green paths 2 cli user interface \033[0m"
    )
    # Define subparsers for different actions
    subparsers = parser.add_subparsers(dest="action", help="")

    # Subparser for preprocessing
    all_pipeline_parser = subparsers.add_parser(
        "all", help="Run the whole/all pipeline."
    )
    all_pipeline_parser.add_argument(
        "-uc",
        "--use_exposure_cache",
        help="If flag is given, use exposure data cache if found from data/cache directory.",
        action="store_true",
    )

    # Subparser for preprocessing
    preprocessing_parser = subparsers.add_parser(
        "preprocessing", help="Run the preprocessing pipeline."
    )

    # Subparser for routing
    routing_parsers = subparsers.add_parser("routing", help="Run the routing pipeline.")

    # Subparser for exposure analysing
    analysing_parsers = subparsers.add_parser(
        "analysing", help="Run the analysing pipeline."
    )

    # OSM PARSER
    osm_segmenter_parser = subparsers.add_parser(
        "segment_osm_network", help="Segment OSM network to smaller parts."
    )

    osm_segmenter_parser.add_argument(
        "-fp",
        "--filepath",
        type=str,
        help="Filepath to osm network file.",
        required=True,
    )

    osm_segmenter_parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Name for the new osm network file, without file extension.",
        required=False,
    )

    # Subparser for validation module
    validation_parsers = subparsers.add_parser(
        "validate", help="Validate user configuration"
    )

    # Subparser for descriptor module
    description_parsers = subparsers.add_parser(
        "describe", help="Validate user configuration"
    )

    description_parsers.add_argument(
        "-sf",
        "--save_to_file",
        help="If flag is given, save the description to a txt file to cache folder. Otherwise print to console.",
        action="store_true",
    )

    # Subparser for descriptor module
    cache_parsers = subparsers.add_parser(
        "clear_db_cache",
        help="Clear db cache based on the given folder names, or all if no names given.",
    )

    cache_parsers.add_argument(
        "-t",
        "--table-names",
        help="Specify one or more table names. To clear all tables, call without -t flag. Example: -t travel_times. Tables to clear are: output_results, routing_results, segment_store and travel_times.",
        nargs="+",
        required=False,
    )

    args, unknown = parser.parse_known_args()

    if args.action == "validate":
        validate_user_config()
    elif args.action == "describe":
        DataDescriptor().describe(args.save_to_file)
    elif args.action == "clear_db_cache":
        clear_db(args.table_names)
    elif args.action == "preprocessing":
        LOG.info("Running preprocessing pipeline. \n\n")
        handle_pipelines("preprocessing")
    elif args.action == "routing":
        LOG.info("Running routing pipeline.")
        handle_pipelines("routing")
    elif args.action == "analysing":
        LOG.info("Running exposure analysing pipeline.")
        handle_pipelines("analysing")
    elif args.action == "all":
        LOG.info("Running the all pipeline.")
        handle_pipelines("all", args.use_exposure_cache)
    elif args.action == "segment_osm_network":
        segment_or_use_cache_osm_network(args.filepath)
    else:
        # print help if no action is given
        parser.print_help()


if __name__ == "__main__":
    main()
