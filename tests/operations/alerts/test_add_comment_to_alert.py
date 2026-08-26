from unittest.mock import patch

from django.conf import settings


def test_add_comment_to_alert(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.alerts.add_comment_to_alert import (
        add_comment_to_alert,
    )

    with patch(
        "sekoia_io_xdr.operations.alerts.add_comment_to_alert.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "unseen": False,
            "created_by_type": "apikey",
            "date": 1670309132,
            "uuid": "fbdeaba1-dd63-496f-b515-9f14a886a51a",
            "author": "ydi",
            "created_by": "a2f80bf3-93a0-485d-b3db-51611825474c",
            "content": "New comment test",
        }
        result = add_comment_to_alert(
            config=connector_config,
            params={
                "uuid": "ALfghiw34ax",
                "content": "New comment test",
                "author": "ydi",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v1/sic/alerts/ALfghiw34ax/comments",
            json={
                "author": "ydi",
                "content": "New comment test",
            },
        )

        assert result is not None
        assert "uuid" in result


def test_add_comment_to_alert_accepts_deprecated_aliases(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.alerts.add_comment_to_alert import (
        add_comment_to_alert,
    )

    with patch(
        "sekoia_io_xdr.operations.alerts.add_comment_to_alert.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "uuid": "fbdeaba1-dd63-496f-b515-9f14a886a51a"
        }

        add_comment_to_alert(
            config=connector_config,
            params={
                "alert_uuid": "ALlegacy01",
                "comment": "Legacy comment field",
                "author": "legacy-author",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v1/sic/alerts/ALlegacy01/comments",
            json={
                "author": "legacy-author",
                "content": "Legacy comment field",
            },
        )
