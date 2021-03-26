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

Before running `npd validate`, make sure you have prepared the repo for validation:
1. install the plugin to the same python environment where `npd validate` is run:
   ```
   cd <plugin path>
   pip install napari-plugin-devtools
   pip install -e .
   ```
2. package the plugin, if skipped we do not run classifier validation, which may cause your plugin not showing 
   up in napari's plugin installation menu. The build process can be different for your plugin, for a typical setup try:
   ```
   python setup.py sdist bdist_wheel
   ```

`npd validate` list function hooks under current python environment, to install plugin from a repo to python 
environment, run `pip install -e <plugin path>`

`npd validate -d|--dist dist` name of the dist, default to first plugin name if not provided, should be provided when 
there are multiple plugins in same package or plugin name is different from package name

`npd validate -v|--verbose` enable verbose mode, gives slightly more information on the underlying 
findings of validation process. By default disabled to avoid the eye sore from too much text.

Output from `npd validate` has multiple sections, where each section is a separate validation where the header
specifies what is being checked, and the last section is the aggregated report of overall status.

1. Hooks validation: check if there are at least one hook implemented by the plugin.
2. Builds validation: check if all builds have correct trove classifiers.
3. Entrypoint validation: check if the specified plugin module is registered as napari plugin in entrypoint.
4. Validation report: if any of the validation is marked as FAILED, see above sections for details



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
