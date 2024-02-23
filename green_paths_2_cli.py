"""Cli user interface for Green paths 2."""

import argparse

from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.data_fetchers.osm_network_loader import (
    download_and_move_osm_pbf,
    get_available_pyrosm_data_sources,
)
from green_paths_2.src.preprocessing.main import preprocessing
from green_paths_2.src.preprocessing.osm_segmenter import segment_osm_network

LOG = setup_logger(__name__, LoggerColors.BLUE.value)


def main():
    print(
        "\n\n  \033[95m Greetings traveller! Welcome to Green paths 2 cli user interface. Please provide an action. \n\n (Use 'action' --help' for information on each actions arguments.) \033[0m"
    )
    parser = argparse.ArgumentParser(
        description="\033[92m Green paths 2 cli user interface \033[0m"
    )
    # Define subparsers for different actions
    subparsers = parser.add_subparsers(dest="action", help="")

    # Subparser for preprocessing
    preprocessing_parser = subparsers.add_parser(
        "preprocessing", help="Run the whole preprocessing pipeline."
    )
    preprocessing_parser.add_argument(
        "-nc",
        "--use_network_cache",
        help="If flag is given, use network cache if found from data/cache directory.",
        action="store_true",
    )

    # Subparser for routing
    routing_parsers = subparsers.add_parser(
        "route", help="Run the whole routing pipeline."
    )
    # Add arguments specific to action2 if needed

    # TODO: add cache to routing?
    routing_parsers.add_argument(
        "-rc",
        "--router_cache",
        help="ROOPE TODO",
        action="store_true",
    )

    # DATA LOADERS
    fetchers_parser = subparsers.add_parser(
        "fetch_osm_network", help="Fetch data from different sources."
    )

    fetchers_parser.add_argument(
        "-a",
        "--area",
        type=str,
        help="Name of city.",
        required=False,
    )

    fetchers_parser.add_argument(
        "-l",
        "--list_available_cities",
        help="Prints all available cities (pyrosm)",
        action="store_true",
        required=False,
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

    args = parser.parse_args()

    if args.action == "preprocessing":
        LOG.info("Running preprocessing pipeline. \n\n")
        preprocessing()
    elif args.action == "route":
        print("TODO: create routing")
    elif args.action == "fetch_osm_network":
        if args.list_available_cities:
            LOG.info(f"Available cities (pyrosm): \n\n")
            get_available_pyrosm_data_sources()
            return
        elif not args.area:
            LOG.error(
                f"Please provide an area name or bounding box coordinates (tuple, minx, miny, maxx, maxy)."
            )
        else:
            LOG.info(f"Fetching OSM network. Using area: {args.area}")
            download_and_move_osm_pbf(args.area)
    elif args.action == "segment_osm_network":
        segment_osm_network(args.filepath, args.name)
    else:
        # print help if no action is given
        parser.print_help()


if __name__ == "__main__":
    main()
