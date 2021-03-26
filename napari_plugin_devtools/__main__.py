"""
napari plugin command line developer tool.
"""
import argparse
import importlib.util as importlib
import os
import sys

from pkg_resources import DistributionNotFound, get_entry_map

from .validation import Options, list_hook_implementations, validate_package


def main():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(
        help='npd validate scans your current python environment to validate '
        'hook registration and entrypoint information, also looks for '
        'built artifacts under dist folder to validate classifiers.'
    )
    validate_parser = sub_parsers.add_parser("validate")
    validate_parser.add_argument(
        'plugins',
        nargs="+",
        help="plugin(s) to validate",
    )
    validate_parser.add_argument(
        "-d",
        "--dist",
        help="name of the dist, default to first plugin name if not provided, "
        "specify when there are multiple plugins in same package or "
        "plugin is different from package name",
    )
    validate_parser.add_argument(
        "-v", "--verbose", action="store_true", help="print verbose report"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        print("----Currently we only support 'npd validate'----")
        parser.exit()

    args = parser.parse_args()

    if args.dist is None:
        args.dist = args.plugins[0]
    error_code = 0

    print("-----------------------------------------------------------------")
    print("Hooks validation:")
    hooks_error = validate_functions(args)

    print("-----------------------------------------------------------------")
    print("Builds validation:")
    package_error = validate_builds(args)

    print("-----------------------------------------------------------------")
    print("Entrypoint validation:")
    entry_error = validate_entries(args)

    print("-----------------------------------------------------------------")

    if hooks_error:
        print("Hooks validation: FAILED")
        error_code = 1
    else:
        print("Hooks validation: PASSED")

    if package_error is None:
        print("Builds validation: SKIPPED")
    elif package_error:
        print("Builds validation: FAILED")
        error_code = 1
    else:
        print("Builds validation: PASSED")

    if entry_error:
        print("Entrypoint validation: FAILED")
        error_code = 1
    else:
        print("Entrypoint validation: PASSED")
    return error_code


def validate_functions(args):
    hooks_errors = validate_hooks(args.plugins, args.verbose)
    hooks_error = False
    if hooks_errors:
        for key, value in hooks_errors.items():
            if value:
                hooks_error = True
                print(f"Error[{key}]: {value}")
    return hooks_error


def validate_builds(args):
    package_error = None
    if os.path.isdir("dist"):
        if not validate_packages("dist", args.verbose):
            package_error = True
            print("Error! Classifier is missing in at least 1 package.")
        else:
            package_error = False
    else:
        print("Skipped classifier validation, no package found. Skipping")
        print("this test may cause user not seeing your plugin in napari")
        print("plugin installation menu. To rerun, Repackage dist folder.")
    return package_error


def validate_entries(args):
    entry_error = False
    for plugin in args.plugins:
        try:
            dist = args.dist
            entry_map = get_entry_map(dist)

            if 'napari.plugin' not in entry_map:
                print(f"Error: Invalid entrypoint for {plugin}")
                print(f"Add 'napari.plugin' to the entrypoint under {plugin}")
                entry_error = True
            else:
                module = entry_map['napari.plugin'][plugin].module_name
                name = entry_map['napari.plugin'][plugin].name
                if plugin != name:
                    print(
                        f"Plugin name not matching, expecting "
                        f"{plugin}, but found {name}"
                    )
                    entry_error = True
                else:
                    spec = importlib.find_spec(module)
                    if spec is None:
                        print(
                            f"Specified module {module} is not found for {plugin}"
                        )
                        entry_error = True
                    else:
                        print(
                            f"Validated entrypoint {module} exists for {plugin}."
                        )
        except DistributionNotFound:
            print(f"Error: Unable to retrive entrypoint for {plugin}.")
            print(f"Check your entrypoint setup to verify {plugin} is added.")
            entry_error = True

    if entry_error:
        print("After your made the proper fix, reinstall the package.")
        print("(Not sure how? try 'pip install -e <plugin folder>')")
    return entry_error


def validate_hooks(plugins, verbose):
    plugin_functions = dict()

    signatures, errors = list_hook_implementations()
    for (option, functions) in signatures.items():
        for function_signature in functions:
            name = function_signature['plugin name']
            if name in plugins:
                if (
                    name in plugin_functions
                    and option in plugin_functions[name]
                ):
                    plugin_functions[name][option].append(function_signature)
                elif name in plugin_functions:
                    plugin_functions[name][option] = [function_signature]
                else:
                    plugin_functions[name] = {option: [function_signature]}

    if plugin_functions:
        print("Plugin hook registration for current environment:")
    for name, mapping in plugin_functions.items():
        for option, signatures in mapping.items():
            if option == Options.function or option == Options.widget:
                print(
                    f'Found {len(signatures)} registered '
                    f'{option.name} hook(s) for {name}:'
                )
                if verbose:
                    print(
                        "-",
                        "\n- ".join(
                            str(signature) for signature in signatures
                        ),
                    )
                else:
                    print(
                        "-",
                        "\n- ".join(
                            signature["function name"]
                            for signature in signatures
                        ),
                    )
            else:
                print(
                    f"Found {len(signatures)} registered "
                    f"{option.name} hook(s) for {name}:"
                )
                if verbose:
                    print(
                        "-",
                        "\n- ".join(
                            str(signature) for signature in signatures
                        ),
                    )
                else:
                    print(
                        "-",
                        "\n- ".join(
                            signature["spec"] for signature in signatures
                        ),
                    )
        print()

    print_tutorial = False

    if len(plugin_functions) == 0:
        if '' in errors:
            errors[''].append("Error! No hook found in current environment.")
        else:
            errors[''] = ["Error! No hook found in current environment."]
        print_tutorial = True

    for plugin in plugins:
        if plugin not in plugin_functions:
            if plugin in errors:
                errors[plugin].append(
                    f"Error! No hook found in current environment for plugin: {plugin}."
                )
            else:
                errors[plugin] = [
                    f"Error! No hook found in current environment for plugin: {plugin}."
                ]
            print_tutorial = True

    if print_tutorial:
        print("Please see tutorial in https://napari.org/docs/dev/plugins/")
        print("to verify your plugin has the correct setup.")
    return errors


def validate_packages(folder, verbose):
    packages_validated = True
    packages = []
    for pkgpath in os.listdir(folder):
        pkgpath = os.path.join(folder, pkgpath)
        packages.append(pkgpath)

    for package in packages:
        package_validated = validate_package(package, verbose=verbose)
        if package_validated:
            print(f'validated {package}')
        packages_validated = packages_validated and package_validated
    return packages_validated


if __name__ == '__main__':
    sys.exit(main())
