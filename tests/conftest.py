import logging
import os
import sys
import types
from pathlib import Path

import pytest
from django.conf import settings
from django.utils.functional import empty

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def _register_connectors_stub() -> None:
    """Provide the minimal FortiSOAR connector symbols used by this project."""

    class ConnectorError(Exception):
        pass

    def get_logger(name: str):
        return logging.getLogger(name)

    connectors_pkg = types.ModuleType("connectors")
    connectors_pkg.__path__ = []

    core_pkg = types.ModuleType("connectors.core")
    core_pkg.__path__ = []

    connector_mod = types.ModuleType("connectors.core.connector")
    setattr(connector_mod, "ConnectorError", ConnectorError)
    setattr(connector_mod, "get_logger", get_logger)

    base_connector_mod = types.ModuleType("connectors.core.base_connector")
    setattr(base_connector_mod, "ConnectorError", ConnectorError)

    sys.modules.setdefault("connectors", connectors_pkg)
    sys.modules.setdefault("connectors.core", core_pkg)
    sys.modules.setdefault("connectors.core.connector", connector_mod)
    sys.modules.setdefault("connectors.core.base_connector", base_connector_mod)


_register_connectors_stub()


@pytest.fixture(autouse=True)
def _reset_django_settings():
    """Tests call settings.configure() repeatedly, so reset settings each time."""
    settings._wrapped = empty
    yield
    settings._wrapped = empty


@pytest.fixture
def connector_config() -> dict:
    return {
        "api_key": os.getenv("api_key"),
        "verify_certificate": True,
        "proxy": True,
    }
