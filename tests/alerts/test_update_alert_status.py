from unittest.mock import patch

from django.conf import settings


def test_update_alert_status(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.alerts.update_alert_status import \
        update_alert_status

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = 200

        result = update_alert_status(
            config=connector_config,
            params={
                "alert_uuid": "Ahytv57q55F",
                "comment": "Validate",
                "action_uuid": "c39a0a95-aa2c-4d0d-8d2e-d3decf426eea",
            },
        )
        assert result == 200
