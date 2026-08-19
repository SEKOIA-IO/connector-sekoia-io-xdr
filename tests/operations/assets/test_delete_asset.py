from unittest.mock import patch

from django.conf import settings


def test_delete_asset(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.assets.delete_asset import delete_asset

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = 201
        result = delete_asset(
            config=connector_config,
            params={"asset_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"},
        )
        assert result is not None
