from unittest.mock import patch

from django.conf import settings


def test_add_comment_to_alert(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.alerts.add_comment_to_alert import \
        add_comment_to_alert

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
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
                "alert_uuid": "ALfghiw34ax",
                "comment": "New comment test",
                "author": "ydi",
            },
        )
        assert result is not None
        assert "uuid" in result
