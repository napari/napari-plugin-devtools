import pytest
from napari.plugins import PluginManager


class _TestPluginManager(PluginManager):
    def assert_plugin_name_registered(self, plugin_name):
        assert plugin_name in self.plugins

    def assert_module_registered(self, module):
        if isinstance(module, str):
            assert module in {m.__name__ for m in self.plugins.values()}
        else:
            assert module in self.plugins.values()

    def assert_implementations_registered(self, plugin, hook_names=()):
        from typing import Collection

        plugin = self._ensure_plugin(plugin)
        regnames = {hook.name for hook in self._plugin2hookcallers[plugin]}
        _hook_names = (
            hook_names
            if isinstance(hook_names, Collection)
            and not isinstance(hook_names, str)
            else [hook_names]
        )
        if not _hook_names:
            if not regnames:
                raise AssertionError(
                    f"No implementations were registered for plugin {plugin!r}"
                )
        else:
            for hook in _hook_names:
                if hook not in regnames:
                    raise AssertionError(
                        f"{hook!r} was not registered for plugin {plugin!r}"
                    )


@pytest.fixture
def napari_plugin_tester():
    """A fixture that can be used to test plugin registration.
    See _TestPluginManager above for tests implementations:
    Examples
    --------
    >>> def test_pm(napari_plugin_tester):
    ...     napari_plugin_tester.assert_plugin_name_registered("test-plugin")
    ...     napari_plugin_tester.assert_module_registered(_test)
    ...     napari_plugin_tester.assert_implementations_registered(
    ...         "test-plugin", "napari_get_reader"
    ...     )
    """
    from napari.plugins import hook_specifications

    pm = _TestPluginManager('napari', discover_entry_point='napari.plugin')
    pm.add_hookspecs(hook_specifications)
    pm.discover()
    return pm
