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
command line interface, and the other is a pytest fixture.

### Command Line Interface (CLI) Usage

see [CLI_usage.md](documentation/CLI_usage.md)


### Pytest fixture usage
devtools provides a pytest fixture: napari_plugin_tester 
in the plugin_tester.py, it extends a plugin manager used by napari
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
