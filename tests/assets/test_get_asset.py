from unittest.mock import patch

from django.conf import settings


def test_get_asset(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.assets.get_asset import get_asset

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
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
        result = get_asset(config=connector_config, params={"asset_uuid": asset_uuid})
        assert result is not None
        assert result["uuid"] == asset_uuid
