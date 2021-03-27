"""
napari plugin command line developer tool.
"""
import argparse
import importlib.util as importlib
import sys

from importlib_metadata import PackageNotFoundError, metadata
from pkg_resources import DistributionNotFound, get_distribution
from termcolor import colored

from .validation import Options, list_hook_implementations

PASSED = colored('PASSED', 'green')
FAILED = colored('FAILED', 'red')


def main():
    args = parse_args()
    print("-" * 64)
    print(
        f"Scanning current python environment: "
        f"{colored(sys.prefix, 'yellow')}"
    )
    return args.func(args)


def validate_hooks(plugin, signatures, errors, verbose):
    hooks = get_hooks_for_plugin(plugin, signatures)
    if len(hooks) > 0:
        print(f"* Hooks registration check - {plugin}:", PASSED)
        if verbose:
            print_hook_report(plugin, hooks, True)
    else:
        errors.append(
            f"Error: No hook registered under "
            f"plugin {plugin}, Please see tutorial in "
            f"https://napari.org/docs/dev/plugins/ to "
            f"verify your plugin setup"
        )
        print(f"* Hooks registration check - {plugin}:", FAILED)


def validate_classifier(classifiers, errors, package, verbose):
    if 'Framework :: napari' in classifiers:
        print("* Classifier check:", PASSED)
    else:
        print("* Classifier check:", FAILED)
        error = (
            f"Error: 'Framework :: napari' does not exist for "
            f"{package}'s {len(classifiers)} known classifier(s)"
        )
        if verbose:
            error = error + f": {classifiers}"

        errors.append(error)


def parse_args():
    parser = argparse.ArgumentParser()
    sub_parsers = parser.add_subparsers(
        help='npd validate scans your current python environment to validate '
        'hook registration and entrypoint information, also looks for '
        'built artifacts under dist folder to validate classifiers.'
    )
    validate_parser = sub_parsers.add_parser("validate")
    validate_parser.set_defaults(func=validate)
    discover_parser = sub_parsers.add_parser("discover")
    discover_parser.set_defaults(func=discover)
    validate_parser.add_argument(
        'packages',
        nargs="+",
        help="package name(s) to validate",
    )
    validate_parser.add_argument(
        "-v", "--verbose", action="store_true", help="print verbose report"
    )
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()
    args = parser.parse_args()
    return args


def validate(args):
    errors = []
    signatures, hook_errors = list_hook_implementations()
    for package in args.packages:
        print("-" * 64)
        print(f"Validating package {package}")

        try:
            classifiers = metadata(package).get_all("Classifier")
            entry_map = get_distribution(package).get_entry_map()
        except PackageNotFoundError or DistributionNotFound:
            print(f"Error: {package} is not found under current environment.")
            print("Install package to current python environment and retry.")
            continue

        validate_classifier(classifiers, errors, package, args.verbose)

        plugins, entrypoint_errors = validate_entrypoint(
            package, entry_map, args.verbose
        )
        errors.extend(entrypoint_errors)

        for plugin in plugins:
            if plugin in hook_errors:
                errors.extend(hook_errors[plugin])
            validate_hooks(plugin, signatures, errors, args.verbose)

    if len(errors) > 0:
        print("-" * 64)
        for error in errors:
            print(error)
            print("-" * 64)
        return 1
    else:
        return 0


def discover(args):
    print("-" * 64)
    signatures, hook_errors = list_hook_implementations()
    plugins = set()

    if len(signatures) == 0:
        print("No Hook found under current environment")
        return 1

    for option, signature in signatures.items():
        for function in signature:
            if 'builtins' != function['plugin name']:
                plugins.add(function['plugin name'])
    for plugin in plugins:
        hooks = get_hooks_for_plugin(plugin, signatures)
        print_hook_report(plugin, hooks, False)
        print("-" * 64)

    if len(hook_errors) > 0:
        for plugin, error in hook_errors.items():
            if len(error) > 0:
                print(f"{plugin}: {error}")
                print("-" * 64)
    return 0


def validate_entrypoint(package, entry_map, verbose):
    errors = []
    plugins = []
    if 'napari.plugin' not in entry_map:
        errors.append(
            f"Error: Invalid entrypoint for package {package}, "
            f"add 'napari.plugin' to the entrypoint under {package}"
        )
        print("* Entrypoint check - syntax:", FAILED)
    else:
        print("* Entrypoint check - syntax:", PASSED)
        plugins = list(entry_map['napari.plugin'].keys())
        if len(plugins) > 0:
            print("* Entrypoint check - plugin registration:", PASSED)
            if verbose:
                print(f"\tPlugins registerd under {package}: {plugins}")
        else:
            errors.append(
                f"Error: No plugin registered for package {package}, "
                f"add plugin module registration under "
                f"'napari.plugin'"
            )
            print("* Entrypoint check - plugin registration:", FAILED)

        module_error = len(plugins) == 0
        for plugin in plugins:
            module = entry_map['napari.plugin'][plugin].module_name
            spec = importlib.find_spec(module)
            if spec is None:
                module_error = True
                errors.append(
                    f"Error: Did not find module {module} for "
                    f"plugin {plugin} under package {package}"
                )
        if module_error:
            print("* Entrypoint check - registered modules exist:", FAILED)
        else:
            print("* Entrypoint check - registered modules exist:", PASSED)
            if verbose:
                modules = [
                    entry_map['napari.plugin'][plugin].module_name
                    for plugin in plugins
                ]
                print(f"\tModules found: {modules}")
    return plugins, errors


def get_hooks_for_plugin(plugin, signatures):
    plugin_functions = dict()

    for (option, functions) in signatures.items():
        for function_signature in functions:
            name = function_signature['plugin name']
            if name == plugin:
                if option in plugin_functions:
                    plugin_functions[option].append(function_signature)
                else:
                    plugin_functions[option] = [function_signature]
    return plugin_functions


def print_hook_report(plugin, hooks, verbose):
    tab = '\t' if verbose else ''
    for option, signatures in hooks.items():
        print(
            f'{tab}Found {len(signatures)} registered '
            f'{option.name} hook(s) for {plugin}:'
        )
        if option == Options.function or option == Options.widget:
            print(
                f"{tab}-",
                f"\n{tab}- ".join(
                    signature["function name"] for signature in signatures
                ),
            )
        else:
            print(
                f"{tab}-",
                f"\n{tab}- ".join(
                    signature["spec"] for signature in signatures
                ),
            )


if __name__ == '__main__':
    sys.exit(main())
