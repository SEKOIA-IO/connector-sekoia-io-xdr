from unittest.mock import patch

import pytest
from django.conf import settings


def test_edit_case(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.cases.edit_case import edit_case

    with patch("connector_sekoia_io_xdr.cases.edit_case.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
            "custom_status_uuid": "b13d8d88-c8f2-4fd1-b863-e4e8f9256fa8",
        }

        result = edit_case(
            config=connector_config,
            params={
                "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "title": "Case title",
                "description": "Case description",
                "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
                "status_name": "Open",
                "priority": "high",
                "tags": "tag1, tag2",
                "subscribers": '[{"avatar_uuid":"0f183f25-5ef0-4f6f-a6e5-fb2d126f18e2","type":"assignee"}]',
                "verdict_uuid": "6e231b66-2ec8-43d2-98de-c8d22b32f3f3",
                "custom_status_uuid": "b13d8d88-c8f2-4fd1-b863-e4e8f9256fa8",
                "custom_priority_uuid": "50ddfcf5-a71c-4f3d-bf7f-8707dbf63825",
                "verdict_analysis": "Likely malicious",
                "verdict_confidence": 85,
            },
        )

        assert result is not None
        action.assert_called_once_with(
            connector_config,
            "PATCH",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            json={
                "title": "Case title",
                "description": "Case description",
                "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
                "status_name": "Open",
                "priority": "high",
                "tags": ["tag1", "tag2"],
                "subscribers": [
                    {
                        "avatar_uuid": "0f183f25-5ef0-4f6f-a6e5-fb2d126f18e2",
                        "type": "assignee",
                    }
                ],
                "verdict_uuid": "6e231b66-2ec8-43d2-98de-c8d22b32f3f3",
                "custom_status_uuid": "b13d8d88-c8f2-4fd1-b863-e4e8f9256fa8",
                "custom_priority_uuid": "50ddfcf5-a71c-4f3d-bf7f-8707dbf63825",
                "verdict_analysis": "Likely malicious",
                "verdict_confidence": 85,
            },
        )


def test_edit_case_with_uuid_only(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.cases.edit_case import edit_case

    with patch("connector_sekoia_io_xdr.cases.edit_case.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"
        }

        edit_case(
            config=connector_config,
            params={"uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"},
        )

        action.assert_called_once_with(
            connector_config,
            "PATCH",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            json={},
        )


def test_edit_case_invalid_subscribers(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.cases.edit_case import edit_case

    with pytest.raises(Exception) as exc_info:
        edit_case(
            config=connector_config,
            params={
                "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "subscribers": "not-a-json-array",
            },
        )

    assert "Invalid `subscribers` format" in str(exc_info.value)
