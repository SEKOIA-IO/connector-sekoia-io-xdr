from unittest.mock import patch

from django.conf import settings


def test_comment_case(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.comment_case import (
        comment_case,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.comment_case.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "fbdeaba1-dd63-496f-b515-9f14a886a51a",
            "content": "New case comment",
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "a2f80bf3-93a0-485d-b3db-51611825474c",
            "created_by_type": "apikey",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        result = comment_case(
            config=connector_config,
            params={
                "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "content": "New case comment",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11/comments",
            json={
                "content": "New case comment",
            },
        )
        assert result is not None
        assert result["uuid"] == "fbdeaba1-dd63-496f-b515-9f14a886a51a"


def test_comment_case_accepts_case_uuid_alias(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.comment_case import (
        comment_case,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.comment_case.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "fbdeaba1-dd63-496f-b515-9f14a886a51a"
        }

        comment_case(
            config=connector_config,
            params={
                "case_uuid": "CASE-ALIAS-001",
                "content": "Alias path parameter",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v1/sic/cases/CASE-ALIAS-001/comments",
            json={
                "content": "Alias path parameter",
            },
        )
