from unittest.mock import patch

from django.conf import settings


def test_get_case(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.cases.get_case import get_case

    with patch("sekoia_io_xdr.operations.cases.get_case.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            "short_id": "CASE-123",
            "title": "Sample case",
            "status": "open",
            "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
            "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
            "created_at": "2024-01-01T00:00:00Z",
            "created_by": "user-1",
            "created_by_type": "apikey",
        }

        result = get_case(
            config=connector_config,
            params={
                "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
                "render": True,
            },
        )

        assert result is not None
        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            params={
                "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
                "render": True,
            },
        )
        assert result["uuid"] == "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"


def test_get_case_default_render(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.cases.get_case import get_case

    with patch("sekoia_io_xdr.operations.cases.get_case.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"
        }

        get_case(
            config=connector_config,
            params={"uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"},
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/cases/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            params={"render": False},
        )
