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
        "-a",
        "--all",
        action="store_true",
        help="validate all package and hooks",
    )
    validate_parser.add_argument(
        "-p",
        "--packages",
        nargs="*",
        help="validate specific package or dist folder",
    )
    validate_parser.add_argument(
        "-k",
        "--hooks",
        nargs="+",
        choices=[option.name for option in Options],
        help="only validate given hooks",
    )
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
        parser.exit()
    args = parser.parse_args()

    packages_validated = True
    hooks_validated = True

    if not args.all and args.packages is None and args.hooks is None:
        validate_parser.print_help()

    if args.all:
        args.hooks = ['reader', 'writer', 'function', 'widget']
        args.packages = []

    if args.packages is not None:
        packages_validated = validate_packages(args)

    if args.hooks:
        hooks_validated = validate_hooks(args)

    if packages_validated and hooks_validated:
        return 0
    elif packages_validated and not hooks_validated:
        return 1
    elif not packages_validated and hooks_validated:
        return 2
    else:
        return 3


def validate_hooks(args):
    errors = []
    hooks_valid = True
    for option in Options:
        if option.name in args.hooks:
            hook_found, hook_valid = validate_hook(
                option, args.verbose, args.include_plugin, args.exclude_plugin
            )
            if not hook_found:
                errors.append(option)
                hooks_valid = hooks_valid and hook_valid
    if (args.all and len(errors) == len(Options)) or (
        not args.all and len(errors) > 0
    ):
        hooks_valid = False
        names = json.dumps(
            {
                option.name: [hook_caller.name for hook_caller in option.value]
                for option in errors
            },
            default=str,
            indent=4,
        )
        print(
            f'No hook found for {args.hooks}, please check the following:\n'
            f'1. Plugin module is registered in entry_points of the project\n'
            f'2. Plugin hook is annotated with @napari_hook_implementation\n'
            f'3. The annotated method are named accordingly: {names}'
        )

    return hooks_valid


def validate_packages(args):
    packages_validated = True
    if len(args.packages) == 0:
        for pkgpath in os.listdir("dist"):
            pkgpath = os.path.join("dist", pkgpath)
            args.packages.append(pkgpath)
    for package in args.packages:
        package_validated = validate_package(package, verbose=args.verbose)
        if package_validated and args.verbose:
            print(f'validated {package}')
        packages_validated = packages_validated and package_validated
    if packages_validated:
        print(f"Success! All {len(args.packages)} packages are validated")
    return packages_validated


def validate_hook(option, verbose, include_plugins, exclude_plugins):
    validated, signatures = list_hook_implementations(
        option, include_plugins, exclude_plugins
    )
    if len(signatures) == 0:
        return False, validated
    else:
        print(f'Found {len(signatures)} {option.name} hooks')
        if verbose:
            signature = json.dumps(signatures, default=str, indent=4)
            print(f'{option.name}: {signature}')
        return True, validated


if __name__ == '__main__':
    sys.exit(main())
