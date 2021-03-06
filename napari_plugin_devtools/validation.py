import enum
import inspect
import json
import os
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


def validate_packages(folder):
    """Validate the packages built for distribution.

    Parameters
    ----------
    folder : str
        dist folder after build with setuptools

    Returns
    ------
    err_code : int
        0 if every package is valid, 1 otherwise
    """
    err_code = 0
    for pkgpath in os.listdir(folder):
        pkgpath = os.path.join(folder, pkgpath)
        if pkgpath.endswith('.tar.gz'):
            dist = SDist(pkgpath)
        elif pkgpath.endswith('.whl'):
            dist = Wheel(pkgpath)
        else:
            print(f'Not a valid format {pkgpath}')
            continue
        if not (
            hasattr(dist, 'classifiers')
            and 'Framework :: napari' in dist.classifiers
        ):
            err_code = 1
            classifiers = '\n\t'.join(dist.classifiers)
            print(
                f'Woops! "Framework :: napari" was not found in {pkgpath}\n'
                f'Know classifiers:\n'
                f'\t{classifiers}\n'
                f'Please update your package setup configuration to include '
                f'"Framework :: napari", then rebuild the distribution.\n'
            )
        else:
            print(f'validated {pkgpath}')
    return err_code


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
    err_code: int
        0 if the function is valid, 1 otherwise
    """
    err_code = 0
    plugin_name = hookimpl.plugin_name
    hook_name = '`napari_experimental_provide_function`'
    if plugin_name is None:
        err_code = 1
        print("No plugin name specified")

    for func in args if isinstance(args, list) else [args]:
        if isinstance(func, tuple):
            err_code = 1
            print(
                "To provide multiple functions please use a LIST of callables"
            )
        elif not isinstance(func, FunctionType):
            err_code = 1
            print(
                f'Plugin {plugin_name!r} provided a non-callable type to '
                f'{hook_name}: {type(func)!r}. Function ignored.'
            )

        # Get function name
        name = func.__name__.replace('_', ' ')

        key = (plugin_name, name)
        if key in functions:
            err_code = 1
            print(
                f"Plugin '{plugin_name}' has already registered a function "
                f"'{name}' which has now been overwritten"
            )
        functions[key] = func

    return err_code


def list_hook_implementations(option, plugin_name=None):
    """
    List hook implementations found when loaded by napari

    Parameters
    ----------
    option : type of the function hook to check
    plugin_name : if provided, only show functions from the given plugin name

    Returns
    -------
    err_code: int
        0 if there is one hook registered and no conflicts found, 1 otherwise
    functions_signatures: str
        Json string for the list of function signatures

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
    err_code = 0
    functions = dict()

    if option == Options.function or option == Options.widget:
        fw_hook = option.value[0]
        res = fw_hook._hookexec(fw_hook, fw_hook.get_hookimpls(), None)
        for result, impl in zip(res.result, res.implementation):
            err_code += validate_function(result, impl, functions)
        for key, value in functions.items():
            spec = inspect.getfullargspec(value)
            if plugin_name is None or plugin_name == key[0]:
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
                if (
                    hook_impl.plugin_name != 'builtins'
                    and hook_impl.plugin_name != 'svg'
                ):  # remove plugins installed by default
                    function_signatures.append(
                        {
                            'plugin name': hook_impl.plugin_name,
                            'spec': hook_impl.specname,
                            'tryfirst': hook_impl.tryfirst,
                            'trylast': hook_impl.trylast,
                        }
                    )

    if len(function_signatures) == 0:
        print(
            f'No hook found under "{option.name}", annotate plugin hooks '
            'and add the module to the entry_points under napari.plugin'
        )
        err_code = 1

    return err_code, json.dumps(function_signatures, default=str)
