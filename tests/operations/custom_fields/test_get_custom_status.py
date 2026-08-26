from unittest.mock import patch

from django.conf import settings


def test_get_custom_status(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.custom_fields.get_custom_status import (
        get_custom_status,
    )

    with patch(
        "sekoia_io_xdr.operations.custom_fields.get_custom_status.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "4ffb485e-cf15-46e9-a95d-66f941308002",
            "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
            "level": 3,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "user-1",
            "created_by_type": "apikey",
            "updated_at": "2024-01-02T00:00:00Z",
            "updated_by": "user-2",
            "updated_by_type": "apikey",
            "stage": "open",
            "label": "Pending Review",
            "description": "Status for pending review",
            "is_used": True,
        }

        result = get_custom_status(
            config=connector_config,
            params={"status_uuid": "4ffb485e-cf15-46e9-a95d-66f941308002"},
        )

        assert result is not None
        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/custom_statuses/4ffb485e-cf15-46e9-a95d-66f941308002",
        )
        assert result["uuid"] == "4ffb485e-cf15-46e9-a95d-66f941308002"
