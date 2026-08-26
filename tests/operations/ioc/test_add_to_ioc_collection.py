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


def test_add_to_ioc_collection_accepts_single_indicator(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"task_id": "single-task"}

        result = add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "domain",
                "indicator": "example.org",
                "valid_for": 2,
            },
        )

        payload = action.call_args.kwargs["json"]
        assert payload["format"] == "domain-name.value"
        assert payload["indicators"] == "example.org"
        assert "valid_until" in payload
        assert result == {"task_id": "single-task"}


def test_add_to_ioc_collection_ip_single_family_returns_single_result(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"task_id": "ipv4-task"}

        result = add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "IP address",
                "indicators": ["198.51.100.10"],
            },
        )

        assert result == {"task_id": "ipv4-task"}


def test_add_to_ioc_collection_rejects_empty_ip_list(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with pytest.raises(Exception, match="Invalid IP indicator"):
        add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "IP address",
                "indicators": ["   "],
            },
        )


def test_add_to_ioc_collection_rejects_invalid_indicators_json(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with pytest.raises(Exception, match="Expected a JSON array for indicators"):
        add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "domain",
                "indicators": '{"not":"array"}',
            },
        )


def test_add_to_ioc_collection_supports_hash_format(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"task_id": "hash-task"}

        add_to_ioc_collection(
            config=connector_config,
            params={
                "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                "indicator_type": "hash",
                "indicator": "d41d8cd98f00b204e9800998ecf8427e",
            },
        )

        payload = action.call_args.kwargs["json"]
        assert payload["format"] == "file.hashes"


def test_add_to_ioc_collection_wraps_non_connector_error(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        add_to_ioc_collection,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.add_to_ioc_collection.GenericAPIAction"
    ) as action:
        action.return_value.run.side_effect = RuntimeError("remote failure")

        with pytest.raises(Exception, match="Error: remote failure"):
            add_to_ioc_collection(
                config=connector_config,
                params={
                    "ioc_collection_id": "ioc-collection--00000000-0000-0000-0000-000000000000",
                    "indicator_type": "domain",
                    "indicator": "example.org",
                },
            )


def test_add_to_ioc_collection_perform_raises_no_valid_ip_with_empty_constructed_input(
    connector_config,
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionOperation,
        AddToIocCollectionParams,
    )

    op = AddToIocCollectionOperation()
    parsed = AddToIocCollectionParams.model_construct(
        ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
        indicator_type="IP address",
        indicator=None,
        indicators=[],
        valid_for=None,
    )

    with pytest.raises(Exception, match="Invalid IP indicator"):
        op.perform(connector_config, parsed)


def test_add_to_ioc_collection_params_parse_indicators_variants():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    parsed_list = AddToIocCollectionParams(
        ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
        indicator_type="domain",
        indicators=["example.org", 123],
    )
    assert parsed_list.indicators == ["example.org", "123"]

    parsed_blank = AddToIocCollectionParams(
        ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
        indicator_type="domain",
        indicator="example.org",
        indicators="   ",
    )
    assert parsed_blank.indicators == []


def test_add_to_ioc_collection_params_rejects_non_array_json_indicators():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    with pytest.raises(Exception, match="Expected a JSON array for indicators"):
        AddToIocCollectionParams(
            ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
            indicator_type="domain",
            indicator="example.org",
            indicators='{"a": 1}',
        )


def test_add_to_ioc_collection_params_rejects_invalid_json_indicators():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    with pytest.raises(Exception, match="Expected a JSON array for indicators"):
        AddToIocCollectionParams(
            ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
            indicator_type="domain",
            indicator="example.org",
            indicators="[not-json]",
        )


def test_add_to_ioc_collection_params_rejects_non_string_non_list_indicators():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    with pytest.raises(Exception, match="Expected a JSON array for indicators"):
        AddToIocCollectionParams(
            ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
            indicator_type="domain",
            indicator="example.org",
            indicators=123,
        )


def test_add_to_ioc_collection_parse_indicators_direct_none_branch():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    assert AddToIocCollectionParams.parse_indicators(None) is None


def test_add_to_ioc_collection_parse_indicators_direct_json_array_branch():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    assert AddToIocCollectionParams.parse_indicators('[1, "a"]') == ["1", "a"]


def test_add_to_ioc_collection_params_requires_indicator_or_indicators():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionParams,
    )

    with pytest.raises(Exception, match="Either indicator or indicators is required"):
        AddToIocCollectionParams(
            ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
            indicator_type="domain",
        )


def test_add_to_ioc_collection_perform_hits_no_valid_ip_branch_with_mocked_resolver(
    connector_config,
    monkeypatch: pytest.MonkeyPatch,
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionOperation,
        AddToIocCollectionParams,
    )

    op = AddToIocCollectionOperation()
    parsed = AddToIocCollectionParams.model_construct(
        ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
        indicator_type="IP address",
        indicator=None,
        indicators=[],
        valid_for=None,
    )

    monkeypatch.setattr(op, "_resolve_indicators", lambda _parsed: [])

    with pytest.raises(Exception, match="No valid IP indicators were provided"):
        op.perform(connector_config, parsed)


def test_add_to_ioc_collection_wraps_validation_error_in_perform(
    connector_config,
    monkeypatch: pytest.MonkeyPatch,
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.add_to_ioc_collection import (
        AddToIocCollectionOperation,
        AddToIocCollectionParams,
    )

    op = AddToIocCollectionOperation()
    parsed = AddToIocCollectionParams.model_construct(
        ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
        indicator_type="domain",
        indicator="example.org",
        indicators=None,
        valid_for=None,
    )

    with pytest.raises(Exception) as exc:
        AddToIocCollectionParams(
            ioc_collection_id="ioc-collection--00000000-0000-0000-0000-000000000000",
            indicator_type="domain",
        )
    validation_error = exc.value

    def _raise_validation(_parsed):
        raise validation_error

    monkeypatch.setattr(op, "build_payload", _raise_validation)

    with pytest.raises(Exception, match="Error: Invalid parameters"):
        op.perform(connector_config, parsed)
