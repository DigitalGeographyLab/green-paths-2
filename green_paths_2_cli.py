"""Cli user interface for Green paths 2."""

import argparse
from src.preprocessing.main import main as preprocessing_main


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
        "--use_network_cache",
        help="If flag is given, use network cache if found from data/cache directory.",
        action="store_true",
    )

    # Subparser for routing
    routing_parsers = subparsers.add_parser("route", help="Description for action2")
    # Add arguments specific to action2 if needed

    routing_parsers.add_argument(
        "--use__test_route",
        help="Iasdf",
        action="store_true",
    )

    args = parser.parse_args()

    if args.action == "preprocessing":
        preprocessing_main(args.use_network_cache)
    elif args.action == "route":
        print("Routing todo...")
    else:
        # print help if no action is given

        parser.print_help()


if __name__ == "__main__":
    main()

# COLORS FOR CLI

# Light Purple:

# Start Color: \033[95m
# End Color: \033[0m
# Green:

# Start Color: \033[92m
# End Color: \033[0m
# Blue:

# Start Color: \033[94m
# End Color: \033[0m
# Cyan:

# Start Color: \033[96m
# End Color: \033[0m
# Orange:

# Unfortunately, there isn't a standard ANSI escape code for orange. ANSI colors are somewhat limited. A close alternative could be a light yellow:
# Start Color: \033[93m
# End Color: \033[0m
# Red:

# Start Color: \033[91m
# End Color: \033[0m
