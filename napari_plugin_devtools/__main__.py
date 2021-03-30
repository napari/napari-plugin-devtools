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
        get_hook_report(plugin, hooks, verbose)
    else:
        errors.append(
            f"Error: No hook registered under "
            f"plugin {plugin}, Please see tutorial in "
            f"https://napari.org/docs/dev/plugins/ to "
            f"verify your plugin setup"
        )
        print(f"* Hooks registration check - {plugin}:", FAILED)


def validate_classifier(classifiers, errors, package, verbose):
    url = (
        "https://napari.org/docs/dev/plugins/for_plugin_developers.html"
        "#step-4-share-your-plugin-with-the-world"
    )
    if 'Framework :: napari' in classifiers:
        print("* Classifier check:", PASSED)
    else:
        print("* Classifier check:", FAILED)
        error = (
            f"Error: 'Framework :: napari' does not exist for "
            f"{package}'s {len(classifiers)} known classifier(s), "
            f"add 'Framework :: napari' to classifier list, see {url}"
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
        'package',
        help="package name to validate",
    )
    validate_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="print verbose report",
    )
    discover_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="print verbose report",
    )
    if len(sys.argv) == 1:
        parser.print_help()
        parser.exit()
    args = parser.parse_args()
    return args


def validate(args):
    errors = []
    verbose = []
    package = args.package
    signatures, hook_errors = list_hook_implementations()
    print("-" * 64)
    print(f"Validating package {package}")

    try:
        classifiers = metadata(package).get_all("Classifier")
        entry_map = get_distribution(package).get_entry_map()
    except PackageNotFoundError or DistributionNotFound:
        print(f"Error: {package} is not found under current environment.")
        print("Install package to current python environment and retry.")
        return 1

    validate_classifier(classifiers, errors, package, verbose)

    plugins = validate_entrypoint(package, entry_map, errors, verbose)

    for plugin in plugins:

        if plugin in hook_errors:
            errors.extend(hook_errors[plugin])
        validate_hooks(plugin, signatures, errors, verbose)

    if args.verbose and verbose:
        print("-" * 64)
        print("verbose output")
        for line in verbose:
            print(line)

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
    verbose = []

    if len(signatures) == 0:
        print("No Hook found under current environment")
        return 1

    for option, signature in signatures.items():
        for function in signature:
            if 'builtins' != function['plugin name']:
                plugins.add(function['plugin name'])
    for plugin in plugins:
        print(f"Plugin found: {plugin}")
        hooks = get_hooks_for_plugin(plugin, signatures)
        get_hook_report(plugin, hooks, verbose)

    if not args.verbose:
        print()
        print("To see registered hooks, enable verbose flag -v")
    if args.verbose and verbose:
        print("-" * 64)
        print("verbose output")
        for line in verbose:
            print(line)

    if len(hook_errors) > 0:
        for plugin, error in hook_errors.items():
            if len(error) > 0:
                print(f"{plugin}: {error}")
                print("-" * 64)
    return 0


def validate_entrypoint(package, entry_map, errors, verbose):
    plugins = []
    url = (
        "https://napari.org/docs/dev/plugins/for_plugin_developers.html"
        "#step-3-make-your-plugin-discoverable"
    )
    if 'napari.plugin' not in entry_map:
        errors.append(
            f"Error: Invalid entrypoint for package {package}, "
            f"add 'napari.plugin' section to the entrypoint under {package}, "
            f"see {url}"
        )
        print("* Entrypoint check - syntax:", FAILED)
    else:
        print("* Entrypoint check - syntax:", PASSED)
        plugins = list(entry_map['napari.plugin'].keys())
        if len(plugins) > 0:
            print("* Entrypoint check - plugin registration:", PASSED)
            verbose.append(f"Plugins registerd under {package}: {plugins}")
        else:
            errors.append(
                f"Error: No plugin registered for package {package}, "
                f"add plugin module registration in entrypoint under section "
                f"'napari.plugin', see {url}"
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
            modules = [
                entry_map['napari.plugin'][plugin].module_name
                for plugin in plugins
            ]
            verbose.append(f"Modules found: {modules}")
    return plugins


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


def get_hook_report(plugin, hooks, verbose):
    for option, signatures in hooks.items():
        verbose.append(
            f'Found {len(signatures)} registered '
            f'{option.name} hook(s) for {plugin}'
        )
        if option == Options.function or option == Options.widget:
            verbose.append(
                "- "
                + "\n- ".join(
                    signature["function name"] for signature in signatures
                )
            )
        else:
            verbose.append(
                "- "
                + "\n- ".join(signature["spec"] for signature in signatures)
            )


if __name__ == '__main__':
    sys.exit(main())
