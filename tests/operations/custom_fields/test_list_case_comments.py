from unittest.mock import patch

from django.conf import settings


def test_list_case_comments(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.list_case_comments import (
        list_case_comments,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.list_case_comments.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "items": [
                {
                    "uuid": "fbdeaba1-dd63-496f-b515-9f14a886a51a",
                    "content": "Case comment",
                    "created_at": "2024-01-01T00:00:00Z",
                    "created_by": "a2f80bf3-93a0-485d-b3db-51611825474c",
                    "created_by_type": "apikey",
                    "updated_at": "2024-01-02T00:00:00Z",
                }
            ],
            "total": 1,
        }

        result = list_case_comments(
            config=connector_config,
            params={
                "case_uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "limit": 10,
                "offset": 5,
                "date[created_at]": "2025-01-01T00:00:00,2025-12-31T23:59:59",
                "match[created_by]": "soc.user",
                "sort": "created_at",
                "direction": "desc",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11/comments",
            params={
                "limit": 10,
                "offset": 5,
                "date[created_at]": "2025-01-01T00:00:00,2025-12-31T23:59:59",
                "match[created_by]": "soc.user",
                "sort": "created_at",
                "direction": "desc",
            },
        )

        assert result is not None
        assert result["total"] == 1


def test_list_case_comments_with_defaults(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.list_case_comments import (
        list_case_comments,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.list_case_comments.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"items": [], "total": 0}

        list_case_comments(
            config=connector_config,
            params={"case_uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"},
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11/comments",
            params={
                "limit": 20,
                "offset": 0,
                "date[created_at]": None,
                "match[created_by]": None,
                "sort": None,
                "direction": None,
            },
        )


def test_list_case_comments_accepts_uuid_alias(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.custom_fields.list_case_comments import (
        list_case_comments,
    )

    with patch(
        "connector_sekoia_io_xdr.operations.custom_fields.list_case_comments.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"items": [], "total": 0}

        list_case_comments(
            config=connector_config,
            params={"uuid": "CASE-ALIAS-001"},
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/cases/CASE-ALIAS-001/comments",
            params={
                "limit": 20,
                "offset": 0,
                "date[created_at]": None,
                "match[created_by]": None,
                "sort": None,
                "direction": None,
            },
        )
