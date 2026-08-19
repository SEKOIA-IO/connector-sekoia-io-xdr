from unittest.mock import patch

import pytest
from django.conf import settings


def test_add_to_ioc_collection_with_domain_indicators(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "task_id": "00000000-0000-0000-0000-000000000000"
        }

        result = add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "domain",
                "indicators": ["www.sekoia.io", "example.org"],
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/ioc-collections/"
            "ioc-collection--00000000-0000-0000-0000-000000000000/indicators/text",
            json={
                "format": "domain-name.value",
                "indicators": "www.sekoia.io\nexample.org",
            },
        )
        assert result["task_id"] == "00000000-0000-0000-0000-000000000000"


def test_add_to_ioc_collection_splits_ipv4_and_ipv6(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.side_effect = [
            {"task_id": "ipv4-task"},
            {"task_id": "ipv6-task"},
        ]

        result = add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "IP address",
                "indicators": ["198.51.100.10", "2001:db8::1"],
            },
        )

        assert action.call_count == 2
        first_call = action.call_args_list[0]
        second_call = action.call_args_list[1]

        assert first_call.args[0] == connector_config
        assert first_call.args[1] == "POST"
        assert first_call.args[2].endswith("/indicators/text")
        assert first_call.kwargs["json"]["format"] == "ipv4-addr.value"
        assert first_call.kwargs["json"]["indicators"] == "198.51.100.10"

        assert second_call.args[0] == connector_config
        assert second_call.args[1] == "POST"
        assert second_call.args[2].endswith("/indicators/text")
        assert second_call.kwargs["json"]["format"] == "ipv6-addr.value"
        assert second_call.kwargs["json"]["indicators"] == "2001:db8::1"

        assert result == {
            "results": [{"task_id": "ipv4-task"}, {"task_id": "ipv6-task"}]
        }


def test_add_to_ioc_collection_rejects_invalid_ip(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch("sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"):
        with pytest.raises(Exception, match="Invalid IP indicator"):
            add_to_ioc_collection(
                config=connector_config,
                params={
                    "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                    "indicator_type": "IP address",
                    "indicators": ["198.51.100.10/32"],
                },
            )
