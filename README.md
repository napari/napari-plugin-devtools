# napari-plugin-devtools

[![License](https://img.shields.io/pypi/l/napari-plugin-devtools.svg?color=green)](https://github.com/napari/napari-plugin-devtools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-plugin-devtools.svg?color=green)](https://pypi.org/project/napari-plugin-devtools)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-demo.svg?color=green)](https://python.org)
[![tests](https://github.com/napari/napari-plugin-devtools/workflows/CI/badge.svg)](https://github.com/napari/napari-plugin-devtools/actions)

A repo with tools and services for [napari plugin](https://napari.org/docs/dev/plugins/index.html) developers

## Validation tool
The validation tools provides automated tests for plugin developers, 
these checks verify that the plugin is available for users of napari 
to install, and would register entry points with napari. 

There are two parts to the validation tool. One part is a 
command line interface and the other is a pytest fixture.

### Command Line Interface (CLI) Usage
The CLI can be used by continuous integration (CI) pipelines to perform a 
quick verification of a plugins setup without any specific input required. 
It serves as a quick "sanity check". (It is also accessible from python in validation.py)

The tool can be run as `npd <cmd>`. There are 2 commands currently:

`npd --validate-packages` should be used after packages are built
for pypi releases, (example: this repo is built by pep517 standard
`pip install pep517 && python -m pep517.build .`).  The validator
checks that all packages built under dist are correctly tagged with
classifier "Framework :: napari". This is recommended for most plugins
unless you do not want your plugin to appear in the napari built-in plugin installation tool.

`npd --validate-functions` verifies that after the plugin is installed 
to current python environment, typically done through `pip install -e .`, 
there is at least one analysis function registered by the plugin, and 
there are no conflicts in name or registration error, it also output 
all registered function signaturesin a json format that can be used 
for further inspection, for example:
```
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
``` 

Multiple cmds in one execution is supported, for example: 
`npd --validate-functions --validate-packages`

### Pytest fixture usage
devtools provides a pytest fixture: napari_plugin_tester 
in plugin_tester.py, it extends a plugin manager used by napari
and have additional assertion modes ready:
```
def test_pm(napari_plugin_tester):
    napari_plugin_tester.assert_plugin_name_registered("test-plugin")
    napari_plugin_tester.assert_module_registered(_test)
    napari_plugin_tester.assert_implementations_registered(
        "test-plugin", "napari_get_reader"
    )
```
where you can check more specifically on a module or function 
being registered under napari annotations, see 
[hook specifications](https://napari.org/docs/dev/plugins/hook_specifications.html)
to find what other annotations are avaiable in addition to `napari_get_reader`
