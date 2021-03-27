import enum
import inspect
from types import FunctionType
from typing import Callable, Dict, List, Union

from napari.plugins import plugin_manager
from napari_plugin_engine import HookImplementation


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
    errors: dict of str to str array
        errors found when validating function.
    """
    errors = {}
    plugin_name = hookimpl.plugin_name
    if plugin_name is None:
        errors[''] = ["Error: No plugin name specified"]
    else:
        errors[plugin_name] = []
    for func in args if isinstance(args, list) else [args]:
        if isinstance(func, tuple):
            errors[plugin_name].append(
                "Error: convert tuple to list " "for multiple callables"
            )
        elif not isinstance(func, FunctionType):
            errors[plugin_name].append(
                f'Error: Plugin {plugin_name!r} provided a non-callable type '
                f': {type(func)!r}. Function ignored.'
            )

        # Get function name
        name = func.__name__.replace('_', ' ')

        key = (plugin_name, name)
        if key in functions:
            errors[plugin_name].append(
                f"Error: Plugin '{plugin_name}' has already registered a "
                f"function '{name}' which has now been overwritten"
            )
        functions[key] = func

    return errors


def list_hook_implementations():
    """
    List hook implementations found when loaded by napari

    Parameters
    ----------

    Returns
    -------
    functions_signatures: dict of option to list
        different types of list of function signatures
    errors: dict of str to str array
        errors found when validating function.

    Example:
    {Options.reader: {
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
    }}
    """
    function_signatures = {}
    errors = {}
    for option in Options:
        functions = dict()
        function_signatures[option] = []
        if option == Options.function or option == Options.widget:
            fw_hook = option.value[0]
            res = fw_hook._hookexec(fw_hook, fw_hook.get_hookimpls(), None)
            for result, impl in zip(res.result, res.implementation):
                for plugin_name, error_messages in validate_function(
                    result, impl, functions
                ).items():
                    if plugin_name in errors:
                        errors[plugin_name].extend(error_messages)
                    else:
                        errors[plugin_name] = error_messages
            for key, value in functions.items():
                spec = inspect.getfullargspec(value)
                function_signatures[option].append(
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
                    function_signatures[option].append(
                        {
                            'plugin name': hook_impl.plugin_name,
                            'spec': hook_impl.specname,
                            'tryfirst': hook_impl.tryfirst,
                            'trylast': hook_impl.trylast,
                        }
                    )

    return function_signatures, errors
