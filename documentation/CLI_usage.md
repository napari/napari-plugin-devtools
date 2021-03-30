# CLI Usage

---
## npd

### Description
napari plugin devtools scans the current python environment to find out details about napari plugin information.
To validate a local folder with plugin code, for example a plugin that is working in progress, first install it,
for example `pip install -e .` and then run npd in the same environment.

### Usage
```
npd [COMMANDS] [ARGS...]
```

### Commands
|Command        |Description                                          |
|---------------|-----------------------------------------------------|
|validate       |validate the given package is correctly setup        |
|discover       |discover all plugins under current python environment|


## npd validate

### Description
Validate package(s) within current python environment, report PASSED or FAILED for each check, 
only return 1 when all checks passed.

### Usage
```
npd validate [Options] <package>
```

### Options
|name, shorthand    |Description                     |
|-------------------|--------------------------------|
|--verbose, -v      |Show more detailed output       |

### Examples

validate without verbose flag
```
$ pip install -e .
$ npd validate napari-demo
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Validating package napari-svg
* Classifier check: FAILED
* Entrypoint check - syntax: PASSED
* Entrypoint check - plugin registration: PASSED
* Entrypoint check - registered modules exist: PASSED
* Hooks registration check - svg: PASSED
----------------------------------------------------------------
Error: 'Framework :: napari' does not exist for napari-demo's 12 known classifier(s), add 'Framework :: napari' to 
classifier list, see https://napari.org/docs/dev/plugins/for_plugin_developers.html#step-4-share-your-plugin-with-the-world
----------------------------------------------------------------
```

validate package with some errors and verbose flag:
```
$ pip install -e .
$ npd validate napari-demo
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Validating package napari-demo
* Classifier check: FAILED
* Entrypoint check - syntax: PASSED
* Entrypoint check - plugin registration: PASSED
* Entrypoint check - registered modules exist: FAILED
* Hooks registration check - napari-demo: PASSED
* Hooks registration check - napari-else: FAILED
----------------------------------------------------------------
verbose output
Plugins registerd under napari-demo: ['napari-demo', 'napari-else']
Found 1 registered function hook(s) for napari-demo
- image arithmetic
----------------------------------------------------------------
Error: 'Framework :: napari' does not exist for napari-demo's 10 known classifier(s), add 'Framework :: napari' to classifier list, see https://napari.org/docs/dev/plugins/for_plugin_developers.html#step-4-share-your-plugin-with-the-world
----------------------------------------------------------------
Error: Did not find module napari_not_exists for plugin napari-else under package napari-demo
----------------------------------------------------------------
Error: No hook registered under plugin napari-else, Please see tutorial in https://napari.org/docs/dev/plugins/ to verify your plugin setup
----------------------------------------------------------------
```

early termination of checks due to package having invalid entrypoint:
```
$ pip install -e .
$ npd validate napari-demo
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Validating package napari-demo
* Classifier check: PASSED
* Entrypoint check - syntax: FAILED
----------------------------------------------------------------
Error: 'Framework :: napari' does not exist for napari-demo's 10 known classifier(s)
----------------------------------------------------------------
Error: Invalid entrypoint for package napari-demo, add 'napari.plugin' section to the entrypoint under napari-demo, see https://napari.org/docs/dev/plugins/for_plugin_developers.html#step-3-make-your-plugin-discoverable
----------------------------------------------------------------
```

early termination of checks due to no plugin registered for package:
```
$ pip install -e .
$ npd validate napari-demo
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Validating package napari-demo
* Classifier check: PASSED
* Entrypoint check - syntax: PASSED
* Entrypoint check - plugin registration: FAILED
* Entrypoint check - registered modules exist: FAILED
----------------------------------------------------------------
Error: No plugin registered for napari-demo, add plugin module registration under 'napari.plugin', see https://napari.org/docs/dev/plugins/for_plugin_developers.html#step-3-make-your-plugin-discoverable
----------------------------------------------------------------
```

---
## npd discover

### Description
Discover plugins in current python environment, and show hook types for each plugin

### Usage
```
$ npd discover [Options]
```

### Options
|name, shorthand    |Description                     |
|-------------------|--------------------------------|
|--verbose, -v      |Show more detailed output       |


### Examples
List plugins under current python environment:
```
$ pip install napari-demo
$ pip install napari-svg
$ pip install napari-hdf5-labels-io
$ npd discover            
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Plugin found: svg
Plugin found: napari-demo
Plugin found: napari-hdf5-labels-io

To see registered hooks, enable verbose flag -v
```

List plugins under current python environment with verbose flag:
```
$ pip install napari-demo
$ pip install napari-svg
$ pip install napari-hdf5-labels-io
$ npd discover -v         
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Plugin found: napari-hdf5-labels-io
Plugin found: svg
Plugin found: napari-demo
----------------------------------------------------------------
verbose output
Found 1 registered reader hook(s) for napari-hdf5-labels-io
- napari_get_reader
Found 1 registered writer hook(s) for napari-hdf5-labels-io
- napari_get_writer
Found 6 registered writer hook(s) for svg
- napari_get_writer
- napari_write_image
- napari_write_labels
- napari_write_points
- napari_write_shapes
- napari_write_vectors
Found 1 registered function hook(s) for napari-demo
- image arithmetic
```
