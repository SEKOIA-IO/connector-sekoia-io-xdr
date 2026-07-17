from unittest.mock import patch

from django.conf import settings


def test_get_custom_verdict(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.get_custom_verdict import (
        get_custom_verdict,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.get_custom_verdict.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "c37221b2-5bbf-46eb-ba16-fb618f7b5282",
            "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
            "level": 4,
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "user-1",
            "created_by_type": "apikey",
            "updated_at": "2024-01-02T00:00:00Z",
            "updated_by": "user-2",
            "updated_by_type": "apikey",
            "stage": "closed",
            "label": "Benign",
            "description": "Benign verdict",
            "is_used": True,
        }

        result = get_custom_verdict(
            config=connector_config,
            params={"verdict_uuid": "c37221b2-5bbf-46eb-ba16-fb618f7b5282"},
        )

        assert result is not None
        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/custom_verdicts/c37221b2-5bbf-46eb-ba16-fb618f7b5282",
        )
        assert result["uuid"] == "c37221b2-5bbf-46eb-ba16-fb618f7b5282"
