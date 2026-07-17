from unittest.mock import patch

from django.conf import settings


def test_list_alerts(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.alerts.list_alerts import list_alerts

    with patch(
        "connector_sekoia_io_xdr.operations.alerts.list_alerts.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
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
                "match[community_uuid]": "8f45f26a-c8d0-483e-bf22-3044d85cd77b",
                "status_uuid": "c39a0a95-aa2c-4d0d-8d2e-d3decf426eea",
                "status_name": "validate",
                "rule_uuid": "ebcb5113-dcd1-4563-8c6c-b52556e2bb27",
                "rule_name": "Feed Enriched",
                "short_id": "ALL1A4SKUiU2",
                "date[created_at]": "2022-01-12T10:00:00Z,2022-01-12T11:00:00Z",
                "visible": False,
                "with_count": False,
                "limit": 5,
                "offset": 2,
            },
        )

        action.assert_called_once_with(
            connector_config,
            "GET",
            "https://app.sekoia.io/api/v1/sic/alerts",
            params={
                "match[community_uuid]": "8f45f26a-c8d0-483e-bf22-3044d85cd77b",
                "match[entity_name]": None,
                "match[entity_uuid]": None,
                "match[status_uuid]": "c39a0a95-aa2c-4d0d-8d2e-d3decf426eea",
                "match[status_name]": "validate",
                "match[type_category]": None,
                "match[type_value]": None,
                "match[source]": None,
                "match[target]": None,
                "match[node]": None,
                "match[stix_object]": None,
                "match[rule_uuid]": "ebcb5113-dcd1-4563-8c6c-b52556e2bb27",
                "match[rule_name]": "Feed Enriched",
                "match[detection_type]": None,
                "match[short_id]": "ALL1A4SKUiU2",
                "match[uuid]": None,
                "match[title]": None,
                "match[asset_uuid]": None,
                "match[urgency_display]": None,
                "match[case_short_id]": None,
                "match[assignee]": None,
                "match[custom_status_uuid]": None,
                "match[verdict_uuid]": None,
                "date[created_at]": "2022-01-12T10:00:00Z,2022-01-12T11:00:00Z",
                "date[updated_at]": None,
                "range[urgency]": None,
                "range[similar]": None,
                "nomatch[asset_uuid]": None,
                "nomatch[entity_uuid]": None,
                "nomatch[rule_uuid]": None,
                "nomatch[rule_name]": None,
                "nomatch[detection_type]": None,
                "nomatch[source]": None,
                "nomatch[target]": None,
                "nomatch[status_uuid]": None,
                "nomatch[stix_object]": None,
                "nomatch[type_value]": None,
                "nomatch[urgency_display]": None,
                "nomatch[assignee]": None,
                "nomatch[custom_status_uuid]": None,
                "nomatch[verdict_uuid]": None,
                "visible": False,
                "is_assigned_to_case": None,
                "similar_to": None,
                "limit": 5,
                "offset": 2,
                "stix": False,
                "cases": False,
                "sort": None,
                "direction": None,
                "with_count": False,
            },
        )
        assert result is not None
        assert "total" in result
        assert result["total"] == 1
        assert "items" in result
        assert result["items"] is not None


def test_list_alerts_backward_compatible_date_aliases(connector_config):
    settings.configure()
    from connector_sekoia_io_xdr.operations.alerts.list_alerts import list_alerts

    with patch(
        "connector_sekoia_io_xdr.operations.alerts.list_alerts.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"items": [], "total": 0}

        list_alerts(
            config=connector_config,
            params={
                "creation_start_date": "2025-01-01T00:00:00",
                "creation_end_date": "2025-12-31T23:59:59",
                "updated_start_date": "2025-01-01T00:00:00",
                "updated_end_date": "2025-12-31T23:59:59",
            },
        )

        called_params = action.call_args.kwargs["params"]
        assert (
            called_params["date[created_at]"]
            == "2025-01-01T00:00:00,2025-12-31T23:59:59"
        )
        assert (
            called_params["date[updated_at]"]
            == "2025-01-01T00:00:00,2025-12-31T23:59:59"
        )
        assert called_params["limit"] == 20
        assert called_params["offset"] == 0
