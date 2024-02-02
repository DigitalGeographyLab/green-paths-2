"""Cli user interface for Green paths 2."""

import argparse

from src.logging import setup_logger, LoggerColors
from src.data.fetchers.osm_network_loader import (
    download_and_move_osm_pbf,
    get_available_pyrosm_data_sources,
)
from src.preprocessing.main import main as preprocessing_main


LOG = setup_logger(__name__, LoggerColors.BLUE.value)


def main():
    print(
        "\n\n  \033[95m Greetings traveller! Welcome to Green paths 2 cli user interface. Please provide an action. \n\n (Use 'action' --help' for information on each actions arguments.) \033[0m"
    )
    parser = argparse.ArgumentParser(
        description="\033[92m Green paths 2 cli user interface \033[0m"
    )
    # Define subparsers for different actions
    subparsers = parser.add_subparsers(dest="action", help="Available actions 1")

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
    routing_parsers = subparsers.add_parser("route", help="Description for action2")
    # Add arguments specific to action2 if needed

    # TODO: add cache to routing?
    routing_parsers.add_argument(
        "-rc",
        "--router_cache",
        help="Iasdf",
        action="store_true",
    )

    # Subparser for preprocessing
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

    args = parser.parse_args()

    if args.action == "preprocessing":
        LOG.info(
            "Running preprocessing pipeline. \nUsing network cache: {args.use_network_cache}}"
        )
        preprocessing_main(args.use_network_cache)
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
    else:
        # print help if no action is given
        parser.print_help()


if __name__ == "__main__":
    main()
