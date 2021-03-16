"""
napari plugin command line developer tool.
"""
import argparse
import json
import os
import sys

from .validation import Options, list_hook_implementations, validate_package


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(help='validate plugins')
    validate_parser = sub_parsers.add_parser("validate")
    validate_parser.add_argument(
        "-i",
        "--include-plugin",
        nargs="+",
        help="only include specified plugins",
    )
    validate_parser.add_argument(
        "-e", "--exclude-plugin", nargs="+", help="exclude specified plugins"
    )
    validate_parser.add_argument(
        "-v", "--verbose", action="store_true", help="print verbose report"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        print("----Currently we only support 'npd validate'----")
        parser.exit()
    args = parser.parse_args()

    hooks = ['reader', 'writer', 'function', 'widget']

    error_code = 0

    print("-----------------------------------------------------------------")
    hooks_validated = validate_hooks(
        hooks, args.verbose, args.include_plugin, args.exclude_plugin
    )

    if hooks_validated:
        print("Success! Validated Function Hooks.")
    else:
        error_code = 1
        print("Error! No hook found in current environment.")
        print("Please see tutorial in https://napari.org/docs/dev/plugins/")
    print("-----------------------------------------------------------------")

    if os.path.isdir("dist"):
        if not validate_packages("dist", args.verbose):
            error_code = 1
            print("Error! Classifier is missing in at least 1 package.")
    else:
        print("Skipped classifier validation, no package found. Skipping")
        print("this test may cause user not seeing your plugin in napari")
        print("plugin installation menu. To rerun, Repackage dist folder.")

    print("-----------------------------------------------------------------")
    return error_code


def validate_hooks(hooks, verbose, include_plugin, exclude_plugin):
    errors = []
    hooks_valid = True
    for option in Options:
        if option.name in hooks:
            hook_found, hook_valid = validate_hook(
                option, verbose, include_plugin, exclude_plugin
            )
            if not hook_found:
                errors.append(option)
                hooks_valid = hooks_valid and hook_valid
    if len(errors) == len(Options):
        hooks_valid = False

    return hooks_valid


def validate_packages(folder, verbose):
    packages_validated = True
    packages = []
    for pkgpath in os.listdir(folder):
        pkgpath = os.path.join(folder, pkgpath)
        packages.append(pkgpath)

    for package in packages:
        package_validated = validate_package(package, verbose=verbose)
        if package_validated and verbose:
            print(f'validated {package}')
        packages_validated = packages_validated and package_validated
    if packages_validated:
        print(f"Success! All {len(packages)} package(s) are validated")
    return packages_validated


def validate_hook(option, verbose, include_plugins, exclude_plugins):
    validated, signatures = list_hook_implementations(
        option, include_plugins, exclude_plugins
    )
    if len(signatures) == 0:
        return False, validated
    else:
        print(f'Found {len(signatures)} {option.name} hook(s)')
        if verbose:
            signature = json.dumps(signatures, default=str, indent=4)
            print(f'{option.name}: {signature}')
        return True, validated


if __name__ == '__main__':
    sys.exit(main())
