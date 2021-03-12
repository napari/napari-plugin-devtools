import enum
import inspect
from types import FunctionType
from typing import Callable, Dict, List, Union

from napari.plugins import plugin_manager
from napari_plugin_engine import HookImplementation
from pkginfo import SDist, Wheel


class Options(enum.Enum):
    """A set of valid arithmetic operations for image_arithmetic."""

    reader = [plugin_manager.hook.napari_get_reader]
    writer = [
        plugin_manager.hook.napari_get_writer,
        plugin_manager.hook.napari_write_image,
        plugin_manager.hook.napari_write_labels,
        plugin_manager.hook.napari_write_points,
        plugin_manager.hook.napari_write_shapes,
        plugin_manager.hook.napari_write_surface,
        plugin_manager.hook.napari_write_vectors,
    ]
    function = [plugin_manager.hook.napari_experimental_provide_function]
    widget = [plugin_manager.hook.napari_experimental_provide_dock_widget]


def validate_package(pkgpath, verbose=False):
    if pkgpath.endswith('.tar.gz'):
        dist = SDist(pkgpath)
    elif pkgpath.endswith('.whl'):
        dist = Wheel(pkgpath)
    else:
        print(f'Error: Not a valid format {pkgpath}')
        return False
    if not (
        hasattr(dist, 'classifiers')
        and 'Framework :: napari' in dist.classifiers
    ):
        print(
            f'Error: "Framework :: napari" was not found in {pkgpath}\n'
            f'Please update your package setup configuration to include '
            f'"Framework :: napari", then rebuild the distribution.'
        )
        if verbose:
            classifiers = '\n\t'.join(dist.classifiers)
            print(f'Know classifiers:\n\t{classifiers}\n')
        return False
    else:
        return True


def validate_function(
    args: Union[Callable, List[Callable]],
    hookimpl: HookImplementation,
    functions: Dict,
):
    """Validate the function is properly implemented in napari supported format

    Parameters
    ----------
    args : Union[Callable, List[Callable]]
        function to validate
    hookimpl : HookImplementation
        implementation of the hook
    functions: Dict
        registered functions

    Returns
    ------
    validated: boolean
        True if the function is valid, False otherwise
    """
    validated = True
    plugin_name = hookimpl.plugin_name
    hook_name = '`napari_experimental_provide_function`'
    if plugin_name is None:
        validated = False
        print("Error: No plugin name specified")

    for func in args if isinstance(args, list) else [args]:
        if isinstance(func, tuple):
            validated = False
            print("Error: convert tuple to list for multiple callables")
        elif not isinstance(func, FunctionType):
            validated = False
            print(
                f'Error: Plugin {plugin_name!r} provided a non-callable type '
                f'to {hook_name}: {type(func)!r}. Function ignored.'
            )

        # Get function name
        name = func.__name__.replace('_', ' ')

        key = (plugin_name, name)
        if key in functions:
            validated = False
            print(
                f"Error: Plugin '{plugin_name}' has already registered a "
                f"function '{name}' which has now been overwritten"
            )
        functions[key] = func

    return validated


def list_hook_implementations(option, include_plugins, exclude_plugins):
    """
    List hook implementations found when loaded by napari

    Parameters
    ----------
    option : Options
        type of the function hook to check
    include_plugins : set[str]
        if provided, only show functions from the given plugin name
    exclude_plugins : set[str]
        if provided, do not show functions from the given set

    Returns
    -------
    validated: boolean
        True if the functions are validated, False otherwise
    functions_signatures: List
        list of function signatures

    Example:
    [{
        "plugin name": "napari-demo",
        "function name": "image arithmetic",
        "args": ["layerA", "operation", "layerB"],
        "annotations": {
            "return": "napari.types.ImageData",
            "layerA": "napari.types.ImageData",
            "operation": "<enum 'Operation'>",
            "layerB": "napari.types.ImageData"
        },
        "defaults": null
    }]
    """
    function_signatures = []
    validated = True
    functions = dict()
    if exclude_plugins is None:
        exclude_plugins = {'builtins', 'svg'}
    else:
        exclude_plugins.add('builtins')
        exclude_plugins.add('svg')  # excluding default installed plugins
    if option == Options.function or option == Options.widget:
        fw_hook = option.value[0]
        res = fw_hook._hookexec(fw_hook, fw_hook.get_hookimpls(), None)
        for result, impl in zip(res.result, res.implementation):
            validated = validated and validate_function(
                result, impl, functions
            )
        for key, value in functions.items():
            spec = inspect.getfullargspec(value)
            if (key[0] not in exclude_plugins) and (
                include_plugins is None or key[0] in include_plugins
            ):
                function_signatures.append(
                    {
                        'plugin name': key[0],
                        'function name': key[1],
                        'args': spec.args,
                        'annotations': spec.annotations,
                        'defaults': spec.defaults,
                    }
                )
    elif option == Options.reader or option == Options.writer:
        for hook_spec in option.value:
            for hook_impl in hook_spec.get_hookimpls():
                if (hook_impl.plugin_name not in exclude_plugins) and (
                    include_plugins is None
                    or hook_impl.plugin_name in include_plugins
                ):
                    function_signatures.append(
                        {
                            'plugin name': hook_impl.plugin_name,
                            'spec': hook_impl.specname,
                            'tryfirst': hook_impl.tryfirst,
                            'trylast': hook_impl.trylast,
                        }
                    )
    return validated, function_signatures
