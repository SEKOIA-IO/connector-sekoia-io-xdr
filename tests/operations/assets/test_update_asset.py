from unittest.mock import patch

from django.conf import settings


def test_update_asset(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.assets.update_asset import update_asset

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
            "name": "test update 1",
            "category": "",
            "description": "",
            "criticity": 23,
            "asset_type": "host",
            "community_uuid": "2783b458-fa16-4869-a11e-6e9d505beb24",
            "owners": [],
            "key_characteristics": [],
            "attributes": [{"name": "custome attr for test", "value": "testValue"}],
            "created_at": "2022-12-06T10:00:00Z",
            "updated_at": "2022-12-06T11:00:00Z",
        }
        result = update_asset(
            config=connector_config,
            params={
                "asset_uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "asset_name": "test update 1",
                "asset_type_uuid": "bd64a9d9-a1d6-45ba-979d-d9dc23f12f92",
                "asset_type_name": "host",
                "asset_criticity": 23,
            },
        )
        assert result is not None
        assert result["uuid"] == "d4e84f5a-877a-41e8-8166-9691a9ecffa3"
