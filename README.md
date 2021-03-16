# napari-plugin-devtools

[![License](https://img.shields.io/pypi/l/napari-plugin-devtools.svg?color=green)](https://github.com/napari/napari-plugin-devtools/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-plugin-devtools.svg?color=green)](https://pypi.org/project/napari-plugin-devtools)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-demo.svg?color=green)](https://python.org)
[![tests](https://github.com/napari/napari-plugin-devtools/workflows/CI/badge.svg)](https://github.com/napari/napari-plugin-devtools/actions)

A repo with tools and services for [napari plugin](https://napari.org/docs/dev/plugins/index.html) developers

## Installation
This tool can be installed via pip: `pip install napari-plugin-devtools`, 
you can also add it to your requirements.txt to be installed with other 
dependencies automatically.

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

The tool can be run as `npd <cmd>`. where currently we support cmd `validate`:

`npd validate`: validate classifiers and function hooks can be recognized by napari.
The validation would run on built packages under dist folder to check if they are annotated
properly with framework classifier, and validate hooks are properly annotated that they can be found
by napari.

`npd validate -i|--include-plugin INCLUDE_PLUGIN [INCLUDE_PLUGIN ...]` run hook checks only on listed plugins, 
this is useful to filter out other plugins on a complicated python environment.


`npd validate -e|--exclude-plugin EXCLUDE_PLUGIN [EXCLUDE_PLUGIN ...]` do not run hook checks on listed plugins, 
this is useful to filter out other plugins on a complicated python environment.

`npd validate -v|--verbose` enable verbose mode, gives slightly more information on the underlying 
findings of validation process.



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
