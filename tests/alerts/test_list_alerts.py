from unittest.mock import patch

from django.conf import settings


def test_list_alerts(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.alerts.list_alerts import list_alerts

    with patch("connector_sekoia_io_xdr.utils.GenericAPIAction.run") as query:
        query.return_value = {
            "items": [
                {
                    "entity": {
                        "uuid": "2783b458-fa16-4869-a11e-6e9d505beb24",
                        "name": "Test",
                    },
                    "urgency": {
                        "value": 20,
                        "criticity": 0,
                        "current_value": 20,
                        "display": "Moderate",
                        "severity": 40,
                    },
                    "number_of_total_comments": 0,
                    "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                    "target": None,
                    "created_by_type": "application",
                    "created_by": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                    "updated_by": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                    "rule": {
                        "type": None,
                        "pattern": "[ipv4-addr:value = '1.1.1.1']",
                        "uuid": "ebcb5113-dcd1-4563-8c6c-b52556e2bb27",
                        "description": "",
                        "name": "Feed Enriched",
                        "severity": 40,
                    },
                    "similar": 11,
                    "title": "Feed Enriched",
                    "details": "",
                    "adversaries": [],
                    "created_at": 1574343159,
                    "stix": {},
                    "updated_at": 1578347133,
                    "ttps": [],
                    "short_id": "ALL1A4SKUiU2",
                    "assets": [],
                    "updated_by_type": "application",
                    "last_seen_at": None,
                    "kill_chain_short_id": "KCXKNfnJupq5",
                    "source": "139.155.1.252",
                    "first_seen_at": "2022-01-12T10-00-00Z",
                    "status": {
                        "uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                        "description": "The alert is waiting for action",
                        "name": "Pending",
                    },
                    "community_uuid": "d4e84f5a-877a-41e8-8166-9691a9ecffa3",
                    "alert_type": {
                        "category": "intrusion-attempts",
                        "value": "brute-force",
                    },
                },
            ],
            "total": 1,
        }

        result = list_alerts(
            config=connector_config,
            params={
                "status_uuid": "c39a0a95-aa2c-4d0d-8d2e-d3decf426eea",
                "status_name": "validate",
                "created_at": "2022-01-12T10-00-00Z",
            },
        )
        assert result is not None
        assert "total" in result
        assert result["total"] == 1
        assert "items" in result
        assert result["items"] is not None
