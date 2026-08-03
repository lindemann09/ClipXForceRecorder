
import argparse

from . import APPNAME, __author__, __version__
from .app import LOGFILE, recorder


def print_info(logfilename:str|None = None):
    print("+" + "-" * 30 + "+")
    print(f"| {APPNAME} {__version__}".ljust(31) + "|")
    print("+" + "-" * 30 + "+")
    if logfilename is not None:
        print(f"Logging to {logfilename}")




def cli():
    """Entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        prog=APPNAME,
        description=f"Command-line interface for {APPNAME} {__version__}",
        epilog=f"Author: {__author__}",
    )

    parser.add_argument("SETTINGS_FILE", nargs="?", default="", help="settings file")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--logfile",
        action="store_true",
        default=False,
        help="show logfile path",
    )

    parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Use mock sensor",
    )

    args = parser.parse_args()

    if args.logfile:
        print(f"Log file: {LOGFILE}")
        return

    print_info(str(LOGFILE))

    if len(args.SETTINGS_FILE) > 0:
        recorder.run(settings_file=args.SETTINGS_FILE, mock_sensor=args.mock)
    else:
        recorder.run(mock_sensor=args.mock)


if __name__ == "__main__":
    cli()
