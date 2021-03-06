"""
napari plugin command line developer tool.
"""
import argparse
import sys

from .validation import Options, list_hook_implementations, validate_packages

print_help = True


def main():
    global print_help

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--validate-packages',
        action="store_true",
        help='validate the build packages is marked as napari plugin',
    )
    parser.add_argument(
        '--validate-readers',
        action="store_true",
        help='validate there is a reader hook implemented',
    )
    parser.add_argument(
        '--validate-writers',
        action="store_true",
        help='validate there is a writer hook implemented',
    )
    parser.add_argument(
        '--validate-functions',
        action="store_true",
        help='validate there is a function hook implemented',
    )
    parser.add_argument(
        '--validate-widgets',
        action="store_true",
        help='validate there is a widget hook implemented',
    )
    args = parser.parse_args()

    err_code = 0
    if args.validate_packages:
        err_code += validate_packages('dist')
        print_help = False

    if args.validate_readers:
        err_code += validate_hook(Options.reader)

    if args.validate_writers:
        err_code += validate_hook(Options.writer)

    if args.validate_functions:
        err_code += validate_hook(Options.function)

    if args.validate_widgets:
        err_code += validate_hook(Options.widget)

    if print_help:
        parser.print_help()
    return err_code


def validate_hook(option):
    global print_help

    err_code, signature = list_hook_implementations(option)
    print(f'{option.name}: {signature}')
    print_help = False
    return err_code


if __name__ == '__main__':
    sys.exit(main())
