from unittest.mock import patch

from django.conf import settings


def test_get_custom_priority(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.get_custom_priority import (
        get_custom_priority,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.get_custom_priority.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "8cd62b13-fc72-48b1-99df-74ccd2dc8cd9",
            "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
            "level": 2,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "user-1",
            "created_by_type": "apikey",
            "updated_at": "2024-01-02T00:00:00Z",
            "updated_by": "user-2",
            "updated_by_type": "apikey",
            "color": "#ff9900",
            "label": "Important",
            "description": "Important priority",
            "is_used": True,
        }

        result = get_custom_priority(
            config=connector_config,
            params={"priority_uuid": "8cd62b13-fc72-48b1-99df-74ccd2dc8cd9"},
        )

        assert result is not None
        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/custom_priorities/8cd62b13-fc72-48b1-99df-74ccd2dc8cd9",
        )
        assert result["uuid"] == "8cd62b13-fc72-48b1-99df-74ccd2dc8cd9"
