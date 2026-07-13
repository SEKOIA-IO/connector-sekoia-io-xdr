from unittest.mock import patch

from django.conf import settings


def test_get_asset(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.get_asset import get_asset

    with patch(
        "connector_sekoia_io_xdr.operations.assets.get_asset.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "name": "DMZ-01",
            "created_at": "2019-11-21T09:40:32.514254+00:00",
            "criticity": {"display": "high", "value": 70},
            "owners": [],
            "asset_type": {
                "name": "network",
                "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            },
            "keys": [
                {
                    "name": "cidr-v4",
                    "value": "172.31.0.0/24",
                    "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
                }
            ],
            "description": "Lan with Web server and proxy",
            "attributes": [],
            "updated_at": None,
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            "category": {
                "name": "technical",
                "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            },
            "community_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
        }
        asset_uuid = "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        result = get_asset(
            config=connector_config,
            params={
                "asset_uuid": asset_uuid,
                "with_telemetry": True,
                "with_compliance": True,
            },
        )
        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v2/asset-management/assets/82aa4cea-41fd-4381-8bb9-7100e7f97460",
            params={"with_telemetry": True, "with_compliance": True},
        )
        assert result is not None
        assert result["uuid"] == asset_uuid


def test_get_asset_defaults(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.get_asset import get_asset

    with patch(
        "connector_sekoia_io_xdr.operations.assets.get_asset.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        }

        get_asset(
            config=connector_config,
            params={"asset_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"},
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v2/asset-management/assets/82aa4cea-41fd-4381-8bb9-7100e7f97460",
            params={"with_telemetry": False, "with_compliance": False},
        )


def test_get_asset_accepts_uuid(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.get_asset import get_asset

    with patch(
        "connector_sekoia_io_xdr.operations.assets.get_asset.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        }

        get_asset(
            config=connector_config,
            params={"uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"},
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v2/asset-management/assets/82aa4cea-41fd-4381-8bb9-7100e7f97460",
            params={"with_telemetry": False, "with_compliance": False},
        )
