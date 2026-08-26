import json
from unittest.mock import patch

import pytest
from django.conf import settings


def test_activate_countermeasure(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
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
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
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
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
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


def test_activate_countermeasure_rejects_invalid_comment_json(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with pytest.raises(Exception, match="Expected a JSON object"):
        activate_countermeasure(
            config=connector_config,
            params={
                "cm_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460",
                "comment": "not-json",
            },
        )


def test_activate_countermeasure_requires_comment_or_content(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with pytest.raises(Exception, match="Either comment or content is required"):
        activate_countermeasure(
            config=connector_config,
            params={"cm_uuid": "82aa4cea-41fd-4381-8bb9-7100e7f97460"},
        )


def test_activate_countermeasure_accepts_comment_dict(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with patch("sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {"uuid": "cm-1"}

        result = activate_countermeasure(
            config=connector_config,
            params={
                "cm_uuid": "cm-1",
                "comment": {"content": "Activate", "author": "bob"},
            },
        )

        assert result["uuid"] == "cm-1"


def test_activate_countermeasure_rejects_blank_comment_string(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with pytest.raises(Exception, match="Expected a JSON object"):
        activate_countermeasure(
            config=connector_config,
            params={"cm_uuid": "cm-1", "comment": "   "},
        )


def test_activate_countermeasure_rejects_comment_json_array(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        activate_countermeasure,
    )

    with pytest.raises(Exception, match="Expected a JSON object"):
        activate_countermeasure(
            config=connector_config,
            params={"cm_uuid": "cm-1", "comment": "[]"},
        )


def test_activate_countermeasure_build_payload_guard_without_comment():
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        ActivateCountermeasureOperation,
        ActivateCountermeasureParams,
    )

    op = ActivateCountermeasureOperation()
    parsed = ActivateCountermeasureParams.model_construct(
        cm_uuid="cm-1",
        comment=None,
        content=None,
        author=None,
    )

    with pytest.raises(ValueError, match="Either comment or content is required"):
        op.build_payload(parsed)


def test_activate_countermeasure_params_accepts_comment_none_with_content():
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        ActivateCountermeasureParams,
    )

    parsed = ActivateCountermeasureParams(cm_uuid="cm-1", comment=None, content="ok")
    assert parsed.comment is not None
    assert parsed.comment.content == "ok"


def test_activate_countermeasure_rejects_invalid_comment_type():
    settings.configure()
    from sekoia_io_xdr.operations.countermeasures.activate_countermeasure import (
        ActivateCountermeasureParams,
    )

    with pytest.raises(Exception, match="Expected a JSON object"):
        ActivateCountermeasureParams(cm_uuid="cm-1", comment=123)
