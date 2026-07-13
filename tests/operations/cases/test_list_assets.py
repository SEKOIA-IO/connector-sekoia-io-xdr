from unittest.mock import patch

from django.conf import settings


def test_list_assets(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.cases.list_assets import list_assets

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "total": 1,
            "has_more": False,
            "items": [
                {
                    "uuid": "a2df3f15-c65f-4d90-8a1b-53af8a57b6cd",
                    "name": "srv-prod-01",
                    "type": "host",
                }
            ],
        }

        result = list_assets(
            config=connector_config,
            params={
                "search": "srv-prod",
                "also_search_in_detection_properties": True,
                "also_search_in_tags": True,
                "uuids": "a2df3f15-c65f-4d90-8a1b-53af8a57b6cd",
                "community_uuids": "7c0bac3f-f2ce-491b-b663-638145078516",
                "type": "host",
                "category": "server",
                "source": "edr",
                "tags": "production,linux",
                "reviewed": True,
                "criticality": 3,
                "sort": "created_at",
                "direction": "desc",
                "with_telemetry": True,
                "incorporate_atoms": True,
                "include_revoked": False,
                "rule_uuid": "60ef2646-a96c-4d78-95bf-88f662f0f333",
                "rule_version": "12",
                "connectors": "2fdbf608-3be2-4b7f-8d89-d14c57dbe3f4",
                "connectors_configuration": "3d2a64c4-d2cb-4dd3-a7a6-804070aa097f",
                "format": "v1",
                "include_intake_formats": True,
                "intake_format_uuids": "8a24e764-2780-4c8f-8388-78039c97f8aa",
                "limit": 10,
                "offset": 5,
            },
        )

        assert result is not None
        assert result["total"] == 1
        assert result["items"][0]["name"] == "srv-prod-01"


def test_list_assets_defaults(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.cases.list_assets import list_assets

    with patch(
        "connector_sekoia_io_xdr.operations.cases.list_assets.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "total": 0,
            "has_more": False,
            "items": [],
        }

        list_assets(config=connector_config, params={})

        action.assert_called_once_with(
            connector_config,
            "get",
            "https://app.sekoia.io/api/v2/asset-management/assets",
            params={
                "search": None,
                "also_search_in_detection_properties": False,
                "also_search_in_tags": False,
                "uuids": None,
                "community_uuids": None,
                "type": None,
                "category": None,
                "source": None,
                "tags": None,
                "reviewed": None,
                "criticality": None,
                "sort": None,
                "direction": None,
                "with_telemetry": False,
                "incorporate_atoms": False,
                "include_revoked": False,
                "rule_uuid": None,
                "rule_version": None,
                "connectors": None,
                "connectors_configuration": None,
                "format": None,
                "include_intake_formats": False,
                "intake_format_uuids": None,
                "limit": 20,
                "offset": 0,
            },
        )
