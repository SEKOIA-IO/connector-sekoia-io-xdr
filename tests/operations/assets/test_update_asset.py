from unittest.mock import patch

import pytest
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


def test_update_asset_parses_csv_fields(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.assets.update_asset import update_asset

    with patch(
        "sekoia_io_xdr.operations.assets.update_asset.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3"
        }
        update_asset(
            config=connector_config,
            params={
                "asset_uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "asset_name": "test update 1",
                "asset_type_uuid": "bd64a9d9-a1d6-45ba-979d-d9dc23f12f92",
                "asset_type_name": "host",
                "asset_criticity": 23,
                "asset_attributes": "a,b",
                "asset_keys": ["k1", "k2"],
                "asset_owners": "alice,bob",
            },
        )

        payload = action.call_args.kwargs["json"]
        assert payload["attributes"] == ["a", "b"]
        assert payload["keys"] == ["k1", "k2"]
        assert payload["owners"] == ["alice", "bob"]


def test_update_asset_params_default_none_csv_fields_to_empty_lists():
    settings.configure()
    from sekoia_io_xdr.operations.assets.update_asset import UpdateAssetParams

    parsed = UpdateAssetParams(
        asset_uuid="asset-1",
        asset_type_uuid="type-1",
        asset_type_name="host",
        asset_name="asset",
        asset_criticity=1,
        asset_attributes=None,
        asset_keys=None,
        asset_owners=None,
    )

    assert parsed.asset_attributes == []
    assert parsed.asset_keys == []
    assert parsed.asset_owners == []


def test_update_asset_rejects_invalid_csv_field_type(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.assets.update_asset import update_asset

    with pytest.raises(Exception, match="Expected a comma-separated string or list"):
        update_asset(
            config=connector_config,
            params={
                "asset_uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "asset_name": "test update 1",
                "asset_type_uuid": "bd64a9d9-a1d6-45ba-979d-d9dc23f12f92",
                "asset_type_name": "host",
                "asset_criticity": 23,
                "asset_attributes": 123,
            },
        )
