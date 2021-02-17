# napari-plugin-devtools

[![License](https://img.shields.io/pypi/l/napari-plugin-devtools.svg?color=green)](https://github.com/napari/napari-plugin-devtools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-plugin-devtools.svg?color=green)](https://pypi.org/project/napari-plugin-devtools)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-demo.svg?color=green)](https://python.org)
[![tests](https://github.com/napari/napari-plugin-devtools/workflows/CI/badge.svg)](https://github.com/napari/napari-plugin-devtools/actions)

A repo with tools and services for [napari plugin](https://napari.org/docs/dev/plugins/index.html) developers

## Validation tool
The validation tools provides more transparency and confidence for 
plugin developers through automated tests, these checks verify that 
the plugin is available for users of napari to install, and would 
register entry points with napari. 

There are two parts to the validation 
tool, one part being CLI and another part being pytest fixture, 

### CLI Usage
CLI can be used by CI/CD pipelines to introduce quick verifications 
of plugin setups without more specific input required, it serves as
a "sanity check". (It is can accessible from python in validation.py)

The tool starts as `npd <cmd>`, there are 2 cmds currently:

`npd --validate-packages` should be used after packages are built
for pypi releases, (example: this repo is built by pep517 standard
`pip install pep517 && python -m pep517.build .`) and the validator
checks that all packages built under dist are correctly tagged with
classifier "Framework :: napari". This is required for most plugins
unless you wish your plugin remain hidden to typical end users.

`npd --validate-functions` verify that after the plugin is installed 
to current python environment, typically done through `pip install -e .`, 
there are at least one analysis function registered by the plugin, and 
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
