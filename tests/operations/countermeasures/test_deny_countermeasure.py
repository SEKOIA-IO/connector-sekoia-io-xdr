from unittest.mock import patch

from django.conf import settings


def test_deny_countermeasure(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.countermeasures.deny_countermeasure import (
        deny_countermeasure,
    )

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "alert_uuid": "2783b458-fa16-4869-a11e-6e9d505beb24",
            "uuid": "dc2e68d2-5978-4bd8-8840-89c7453f16f5",
            "relevance": 10,
            "model_uuid": "bd64a9d9-a1d6-45ba-979d-d9dc23f12f92",
            "dynamic_relevance": 11,
            "duration": "100",
            "created_at": "2022-12-06T10:00:00Z",
            "created_by_type": "avatar",
            "activated_at": None,
            "activated_by": None,
            "activated_by_type": None,
            "denied_at": "2022-12-06T10:01:00Z",
            "denied_by": "ydi",
            "denied_by_type": "avatar",
            "action_steps": [],
            "name": "Test",
            "description": "",
            "comments": "",
            "assignee": "",
            "type": "text",
            "external_ref": "",
        }
        result = deny_countermeasure(
            config=connector_config,
            params={
                "countermeasure_uuid": "dc2e68d2-5978-4bd8-8840-89c7453f16f5",
                "content": "bar",
                "author": "ydi",
            },
        )
        assert result is not None
        assert "uuid" in result
        assert result["uuid"] == "dc2e68d2-5978-4bd8-8840-89c7453f16f5"
        assert result["activated_at"] is None
        assert result["denied_at"] is not None
