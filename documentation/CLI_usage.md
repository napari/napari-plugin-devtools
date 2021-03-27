# CLI Usage

---
## npd

### Description
napari plugin devtools scans the current python environment to find out details about napari plugin information.

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
npd validate [Options] <package> [<packages>...]
```

### Options
|name, shorthand    |Description                     |
|-------------------|--------------------------------|
|--verbose, -v      |Show more detailed output       |

### Examples

validate single package
```
$ pip install napari-svg
$ npd validate napari-svg
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
Error: 'Framework :: napari' does not exist for napari-svg's 12 known classifier(s)
----------------------------------------------------------------
```

validate multiple packages with verbose output:
```
$ pip install napari-svg
$ pip install napari-demo
$ npd validate napari-svg napari-demo -v
----------------------------------------------------------------
Scanning current python environment: /Library/Frameworks/Python.framework/Versions/3.8
----------------------------------------------------------------
Validating package napari-svg
* Classifier check: FAILED
* Entrypoint check - syntax: PASSED
* Entrypoint check - plugin registration: PASSED
        Plugins registerd under napari-svg: ['svg']
* Entrypoint check - registered modules exist: PASSED
        Modules found: ['napari_svg']
* Hooks registration check - svg: PASSED
        Found 6 registered writer hook(s) for svg:
        - napari_get_writer
        - napari_write_image
        - napari_write_labels
        - napari_write_points
        - napari_write_shapes
        - napari_write_vectors
----------------------------------------------------------------
Validating package napari-demo
* Classifier check: PASSED
* Entrypoint check - syntax: PASSED
* Entrypoint check - plugin registration: PASSED
        Plugins registerd under napari-demo: ['napari-demo', 'napari-else']
* Entrypoint check - registered modules exist: PASSED
        Modules found: ['napari_demo', 'napari_else']
* Hooks registration check - napari-demo: PASSED
        Found 1 registered function hook(s) for napari-demo:
        - image arithmetic
* Hooks registration check - napari-else: PASSED
        Found 1 registered function hook(s) for napari-else:
        - image arithmetic other
----------------------------------------------------------------
Error: 'Framework :: napari' does not exist for napari-svg's 12 known classifier(s): ['Development Status :: 4 - Beta', 'Intended Audience :: Developers', 'Topic :: Software Development :: Testing', 'Programming Language :: Python', 'Programming Language :: Python :: 3', 'Programming Language :: Python :: 3.6', 'Programming Language :: Python :: 3.7', 'Programming Language :: Python :: 3.8', 'Programming Language :: Python :: Implementation :: CPython', 'Programming Language :: Python :: Implementation :: PyPy', 'Operating System :: OS Independent', 'License :: OSI Approved :: BSD License']
----------------------------------------------------------------
```

validate package with some errors:
```
$ pip install napari-demo
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
Error: 'Framework :: napari' does not exist for napari-demo's 10 known classifier(s)
----------------------------------------------------------------
Error: Did not find module napari_not_exists for plugin napari-else under package napari-demo
----------------------------------------------------------------
Error: No hook registered under plugin napari-else, Please see tutorial in https://napari.org/docs/dev/plugins/ to verify your plugin setup
----------------------------------------------------------------
```

early termination of checks due to package having invalid entrypoint:
```
$ pip install napari-demo
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
Error: Invalid entrypoint for package napari-demo, add 'napari.plugin' to the entrypoint under napari-demo
----------------------------------------------------------------
```
```
$ pip install napari-demo
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
Error: No plugin registered for napari-demo, add plugin module registration under 'napari.plugin'
----------------------------------------------------------------
```

---
## npd discover

### Description
Discover plugins in current python environment, and show hook types for each plugin

### Usage
```
$ npd discover
```

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
Found 1 registered function hook(s) for napari-demo:
- image arithmetic
----------------------------------------------------------------
Found 6 registered writer hook(s) for svg:
- napari_get_writer
- napari_write_image
- napari_write_labels
- napari_write_points
- napari_write_shapes
- napari_write_vectors
----------------------------------------------------------------
Found 1 registered function hook(s) for napari-else:
- image arithmetic other
----------------------------------------------------------------
Found 1 registered reader hook(s) for napari-hdf5-labels-io:
- napari_get_reader
Found 1 registered writer hook(s) for napari-hdf5-labels-io:
- napari_get_writer
----------------------------------------------------------------

```
