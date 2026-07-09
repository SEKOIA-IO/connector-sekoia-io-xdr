from unittest.mock import patch

from django.conf import settings


def test_search_cases(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.cases.search_cases import search_cases

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "total": 1,
            "has_more": False,
            "items": [
                {
                    "uuid": "5de59f97-4fca-47f0-9cc8-c0761f24f5b0",
                    "short_id": "CASE-42",
                    "title": "Phishing investigation",
                    "status": "Open",
                    "status_uuid": "4ad8ea4d-9247-4db1-970f-bf0af13f8888",
                    "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
                }
            ],
        }

        result = search_cases(
            config=connector_config,
            params={
                "community_uuid": "7c0bac3f-f2ce-491b-b663-638145078516",
                "status_uuid": "4ad8ea4d-9247-4db1-970f-bf0af13f8888",
                "status_name": "Open",
                "created_at": "2025-01-01T00:00:00,2025-12-31T23:59:59",
                "created_by": "automation",
                "tags": "phishing",
                "assignees": "analyst@example.org",
                "limit": 10,
                "offset": 5,
                "sort": "created_at",
                "direction": "desc",
            },
        )

        assert result is not None
        assert result["total"] == 1
        assert result["items"][0]["short_id"] == "CASE-42"



def test_search_cases_defaults(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.cases.search_cases import search_cases

    with patch("connector_sekoia_io_xdr.cases.search_cases.GenericAPIAction") as action:
        action.return_value.run.return_value = {"total": 0, "has_more": False, "items": []}

        search_cases(config=connector_config, params={})

        action.assert_called_once_with(
            connector_config,
            "get",
            "https://app.sekoia.io/api/v1/sic/cases",
            params={
                "match[community_uuid]": None,
                "match[status_uuid]": None,
                "match[status_name]": None,
                "date[created_at]": None,
                "match[created_by]": None,
                "match[tags]": None,
                "match[assignees]": None,
                "limit": 20,
                "offset": 0,
                "sort": None,
                "direction": None,
            },
        )
