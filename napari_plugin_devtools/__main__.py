"""
napari plugin command line developer tool.
"""
import argparse
import sys

from .validation import list_function_implementations, validate_packages


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--validate-packages',
        action="store_true",
        help='validate the build packages is marked as napari plugin',
    )
    parser.add_argument(
        '--validate-functions',
        action="store_true",
        help='validate the build packages is marked as napari plugin',
    )
    args = parser.parse_args()

    if args.validate_packages:
        validate_packages('dist')

    if args.validate_functions:
        print(list_function_implementations())


if __name__ == '__main__':
    sys.exit(main())
