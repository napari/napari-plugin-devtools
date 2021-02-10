import inspect
import json
import os
from types import FunctionType
from typing import Callable, Dict, List, Tuple, Union

from napari.plugins import plugin_manager
from napari_plugin_engine import HookImplementation
from pkginfo import SDist, Wheel

functions: Dict[Tuple[str, str], Callable] = dict()


def validate_packages(folder):
    """Validate the packages built for distribution.

    Parameters
    ----------
    folder : str
        dist folder after build with setuptools

    Raises
    ------
    AssertionError
        If the package is not annotated properly
    """
    for pkgpath in os.listdir(folder):
        pkgpath = os.path.join(folder, pkgpath)
        if pkgpath.endswith('.tar.gz'):
            dist = SDist(pkgpath)
        elif pkgpath.endswith('.whl'):
            dist = Wheel(pkgpath)
        else:
            print(f'Not a valid format {pkgpath}')
            continue
        assert (
            hasattr(dist, 'classifiers')
            and 'Framework :: napari' in dist.classifiers
        ), (
            'Classifier Framework :: napari must be specified '
            'for the plugin to be discovered'
        )

        print(f'validated {pkgpath}')


def validate_function(
    args: Union[Callable, List[Callable]],
    hookimpl: HookImplementation,
):
    """Validate the function is properly implemented in napari supported format

    Parameters
    ----------
    args : Union[Callable, List[Callable]]
        function to validate
    hookimpl : HookImplementation
        implementation of the hook

    Raises
    ------
    AssertionError
        When function is not in supported format
    """
    plugin_name = hookimpl.plugin_name
    hook_name = '`napari_experimental_provide_function`'

    assert plugin_name is not None, "No plugin name specified"
    for func in args if isinstance(args, list) else [args]:
        assert not isinstance(
            func, tuple
        ), "To provide multiple functions please use a LIST of callables"
        assert isinstance(func, FunctionType), (
            f'Plugin {plugin_name!r} provided a non-callable type to '
            f'{hook_name}: {type(func)!r}. Function ignored.'
        )

        # Get function name
        name = func.__name__.replace('_', ' ')

        key = (plugin_name, name)
        assert key not in functions, (
            "Plugin '{}' has already registered a function '{}' "
            "which has now been overwritten".format(*key)
        )

        functions[key] = func


def list_function_implementations(plugin_name=None):
    """
    List function implementations found when loaded by napari

    Parameters
    ----------
    plugin_name : if provided, only show functions from the given plugin name

    Returns
    -------
    json string for the list of function signatures

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
    fw_hook = plugin_manager.hook.napari_experimental_provide_function
    functions.clear()
    fw_hook.call_historic(result_callback=validate_function, with_impl=True)
    function_signatures = []
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
    assert len(function_signatures) > 0, (
        'No function found under the entrypoint, annotate plugin function '
        'and add the module to the entry_points under napari.plugin'
    )
    return json.dumps(function_signatures, default=str)
