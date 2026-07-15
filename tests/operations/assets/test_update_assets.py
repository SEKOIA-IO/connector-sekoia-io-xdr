from unittest.mock import patch

import pytest
from django.conf import settings


def test_update_assets(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.update_assets import update_assets

    with patch(
        "connector_sekoia_io_xdr.operations.assets.update_assets.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
            "name": "test update 1",
            "category": "technical",
            "description": "Updated asset",
            "criticality": 23,
            "type": "host",
            "community_uuid": "2783b458-fa16-4869-a11e-6e9d505beb24",
            "props": {"location": "paris"},
            "atoms": {"hostname": "dmz-01"},
            "tags": ["critical", "dmz"],
            "reviewed": True,
            "revoked": False,
            "created_at": "2022-12-06T10:00:00Z",
            "updated_at": "2022-12-06T11:00:00Z",
        }
        result = update_assets(
            config=connector_config,
            params={
                "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "name": "test update 1",
                "type": "host",
                "criticality": 23,
                "description": "Updated asset",
                "category": "technical",
                "entity_uuid": "fd6e4d31-0bb8-43a0-bacb-62d17ac13a0d",
                "props": '{"location":"paris"}',
                "atoms": '{"hostname":"dmz-01"}',
                "tags": "critical, dmz",
                "reviewed": True,
                "revoked": False,
            },
        )

        action.assert_called_once_with(
            connector_config,
            "PUT",
            "https://app.sekoia.io/api/v2/asset-management/assets/d4e84f5a-877a-41e8-8166-9691a9ecffa3",
            json={
                "atoms": {"hostname": "dmz-01"},
                "category": "technical",
                "criticality": 23,
                "description": "Updated asset",
                "entity_uuid": "fd6e4d31-0bb8-43a0-bacb-62d17ac13a0d",
                "name": "test update 1",
                "props": {"location": "paris"},
                "reviewed": True,
                "revoked": False,
                "tags": ["critical", "dmz"],
                "type": "host",
            },
        )

        assert result is not None
        assert result["uuid"] == "d4e84f5a-877a-41e8-8166-9691a9ecffa3"


def test_update_assets_with_uuid_only(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.update_assets import update_assets

    with patch(
        "connector_sekoia_io_xdr.operations.assets.update_assets.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3"
        }

        update_assets(
            config=connector_config,
            params={"uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3"},
        )

        action.assert_called_once_with(
            connector_config,
            "PUT",
            "https://app.sekoia.io/api/v2/asset-management/assets/d4e84f5a-877a-41e8-8166-9691a9ecffa3",
            json={},
        )


def test_update_assets_rejects_legacy_parameters(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.update_assets import update_assets

    with pytest.raises(Exception) as exc_info:
        update_assets(
            config=connector_config,
            params={
                "asset_uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "asset_name": "legacy name",
                "asset_type_name": "network",
                "asset_criticity": 12,
                "asset_description": "legacy description",
            },
        )

    assert "Error: Invalid parameters:" in str(exc_info.value)
    assert "uuid" in str(exc_info.value)


def test_update_assets_invalid_props(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.assets.update_assets import update_assets

    with pytest.raises(Exception) as exc_info:
        update_assets(
            config=connector_config,
            params={
                "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                "props": "not-a-json-object",
            },
        )

    assert "Error: Invalid parameters:" in str(exc_info.value)
    assert "Expected a JSON object." in str(exc_info.value)
