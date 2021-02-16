pytest_plugins = "pytester"


def test_napari_plugin_tester(testdir):
    """Make sure that our napari_plugin_tester fixture works."""

    # create a temporary pytest test file
    testdir.makepyfile(
        """
        from napari_plugin_engine import napari_hook_implementation
        class Plugin:
            @napari_hook_implementation
            def napari_get_reader(path):
                pass
        def test_pm(napari_plugin_tester):
            napari_plugin_tester.register(Plugin)
            napari_plugin_tester.assert_plugin_name_registered("Plugin")
            napari_plugin_tester.assert_module_registered(Plugin)
            napari_plugin_tester.assert_implementations_registered(
                Plugin, "napari_get_reader"
            )
    """
    )
    # run all tests with pytest
    result = testdir.runpytest()

    # check that all 1 test passed
    result.assert_outcomes(passed=1)
