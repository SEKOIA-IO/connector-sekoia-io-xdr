from scripts.cli_utils import configure_script_logger


def test_cli_utils_shim_exports_configure_script_logger():
    logger = configure_script_logger("shim-test")
    assert logger is not None
    assert logger.name == "shim-test"
