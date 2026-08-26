from unittest.mock import patch

from django.conf import settings


def test_edit_alert(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.alerts.edit_alert import edit_alert

    with patch("sekoia_io_xdr.operations.alerts.edit_alert.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
        }

        result = edit_alert(
            config=connector_config,
            params={
                "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
                "alert_type_category": "Suspicious activity",
                "alert_type_value": "Credential access",
                "details": "Updated details",
                "urgency": 70,
                "kill_chain_short_id": "Lateral Movement",
                "title": "Updated alert title",
                "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
                "comment": "Handled by SOC",
                "verdict_analysis": "Likely malicious",
                "verdict_confidence": 90,
                "assignee": "a2f80bf3-93a0-485d-b3db-51611825474c",
                "verdict_uuid": "6e231b66-2ec8-43d2-98de-c8d22b32f3f3",
                "custom_status_uuid": "b13d8d88-c8f2-4fd1-b863-e4e8f9256fa8",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "PATCH",
            "https://app.sekoia.io/api/v1/sic/alerts/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            json={
                "alert_type_category": "Suspicious activity",
                "alert_type_value": "Credential access",
                "details": "Updated details",
                "urgency": 70,
                "kill_chain_short_id": "Lateral Movement",
                "title": "Updated alert title",
                "status_uuid": "8b4d77f8-9c6d-4a67-8d1f-8f6f7c4f5d10",
                "comment": "Handled by SOC",
                "verdict_analysis": "Likely malicious",
                "verdict_confidence": 90,
                "assignee": "a2f80bf3-93a0-485d-b3db-51611825474c",
                "verdict_uuid": "6e231b66-2ec8-43d2-98de-c8d22b32f3f3",
                "custom_status_uuid": "b13d8d88-c8f2-4fd1-b863-e4e8f9256fa8",
            },
        )

        assert result is not None


def test_edit_alert_with_uuid_only(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.alerts.edit_alert import edit_alert

    with patch("sekoia_io_xdr.operations.alerts.edit_alert.GenericAPIAction") as action:
        action.return_value.run.return_value = {
            "uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"
        }

        edit_alert(
            config=connector_config,
            params={"uuid": "b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11"},
        )

        action.assert_called_once_with(
            connector_config,
            "PATCH",
            "https://app.sekoia.io/api/v1/sic/alerts/b6ae1cf7-2f6d-4cb1-8f2d-2f6e37a2cc11",
            json={},
        )


def test_edit_alert_accepts_alert_uuid_alias(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.alerts.edit_alert import edit_alert

    with patch("sekoia_io_xdr.operations.alerts.edit_alert.GenericAPIAction") as action:
        action.return_value.run.return_value = {"uuid": "ALlegacy01"}

        edit_alert(
            config=connector_config,
            params={
                "alert_uuid": "ALlegacy01",
                "urgency": 42,
                "comment": "Legacy uuid alias",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "PATCH",
            "https://app.sekoia.io/api/v1/sic/alerts/ALlegacy01",
            json={
                "urgency": 42,
                "comment": "Legacy uuid alias",
            },
        )
