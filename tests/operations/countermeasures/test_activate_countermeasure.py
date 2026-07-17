import json
from unittest.mock import patch

from django.conf import settings


def test_activate_countermeasure(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
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
            "activated_at": "2022-12-06T10:01:00Z",
            "activated_by": "ydi",
            "activated_by_type": "avatar",
            "denied_at": None,
            "denied_by": None,
            "denied_by_type": None,
            "action_steps": [],
            "name": "Test",
            "description": "",
            "comments": "",
            "assignee": "",
            "type": "text",
            "external_ref": "",
        }
        result = activate_countermeasure(
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
        assert result["activated_at"] is not None
        assert result["denied_at"] is None


def test_activate_countermeasure_with_canonical_comment_json(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            "activated_at": "2026-07-17T00:00:00Z",
        }

        result = activate_countermeasure(
            config=connector_config,
            params={
                "cm_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
                "comment": json.dumps({"content": "Activate", "author": "alice"}),
            },
        )

        assert result is not None
        assert result["uuid"] == "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        assert result["activated_at"] == "2026-07-17T00:00:00Z"


def test_activate_countermeasure_with_deprecated_parameters(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
            "activated_at": "2026-07-17T00:00:00Z",
        }

        result = activate_countermeasure(
            config=connector_config,
            params={
                "countermeasure_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
                "content": "Activate",
                "author": "alice",
            },
        )

        assert result is not None
        assert result["uuid"] == "82aa4cea-41fd-4381-8bb9-7100e7f97460"
        assert result["activated_at"] == "2026-07-17T00:00:00Z"
