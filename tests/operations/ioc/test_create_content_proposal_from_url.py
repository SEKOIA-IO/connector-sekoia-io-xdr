from unittest.mock import patch

from django.conf import settings


def test_create_content_proposal_from_url(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_url import (
        create_content_proposal_from_url,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal_from_url.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "data": {
                "content_proposal_id": "cp-url-001",
                "file_name": "report-url.json",
            }
        }

        result = create_content_proposal_from_url(
            config=connector_config,
            params={
                "url": "https://example.org/report",
                "source_ref": "source-001",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/reports/url",
            params={"source_ref": "source-001"},
            json={"url": "https://example.org/report"},
        )
        assert result["content_proposal_id"] == "cp-url-001"
