import pytest
from sekoia_io_xdr.operations.base import (
    DeprecatedAliases,
    InputModel,
    Operation,
)


class _NoopParams(InputModel):
    uuid: str


class _NoopOperation(Operation):
    http_method = "GET"
    payload_parameter = "params"
    input_model = _NoopParams

    def build_endpoint(self, parsed_input: _NoopParams) -> str:
        return f"https://example.test/{parsed_input.uuid}"

    def build_payload(self, parsed_input: _NoopParams) -> dict:
        return {"q": "ok"}


def test_base_operation_executes_with_standard_structure(connector_config):
    class FakeAction:
        def __init__(self, *_args, **_kwargs):
            self.kwargs = _kwargs

        def run(self):
            return {"ok": True, "kwargs": self.kwargs}

    op = _NoopOperation(api_action_cls=FakeAction)
    result = op.execute(connector_config, {"uuid": "abc"})

    assert result["ok"] is True
    assert result["kwargs"]["params"] == {"q": "ok"}


class _AliasParams(InputModel):
    pass


class _AliasOperation(Operation):
    input_model = _AliasParams
    deprecated_aliases = DeprecatedAliases(
        single={"match[rule_name]": "rule_name"},
        range={"date[created_at]": ("creation_start_date", "creation_end_date")},
    )

    def build_endpoint(self, parsed_input: _AliasParams) -> str:
        return "https://example.test"

    def build_payload(self, parsed_input: _AliasParams) -> dict:
        return {}


def test_deprecated_parameters_are_auto_built_from_aliases():
    assert _AliasOperation.deprecated_parameters["rule_name"] == "match[rule_name]"
    assert (
        _AliasOperation.deprecated_parameters["creation_start_date"]
        == "date[created_at]"
    )
    assert (
        _AliasOperation.deprecated_parameters["creation_end_date"] == "date[created_at]"
    )


def test_resolve_payload_value_prefers_current_field_over_deprecated_aliases():
    op = _AliasOperation()
    params = {
        "match[rule_name]": "Current",
        "rule_name": "Deprecated",
    }

    assert op.resolve_payload_value(params, "match[rule_name]") == "Current"


def test_resolve_payload_value_falls_back_to_single_deprecated_alias():
    op = _AliasOperation()
    params = {"rule_name": "Legacy"}

    assert op.resolve_payload_value(params, "match[rule_name]") == "Legacy"


def test_resolve_payload_value_falls_back_to_range_deprecated_aliases():
    op = _AliasOperation()
    params = {
        "creation_start_date": "2025-01-01T00:00:00",
        "creation_end_date": "2025-01-31T23:59:59",
    }

    assert (
        op.resolve_payload_value(params, "date[created_at]")
        == "2025-01-01T00:00:00,2025-01-31T23:59:59"
    )


def test_resolve_payload_value_returns_default_when_missing():
    op = _AliasOperation()

    assert op.resolve_payload_value({}, "limit", default=20) == 20


def test_resolve_payload_value_can_treat_falsy_as_missing():
    op = _AliasOperation()

    assert (
        op.resolve_payload_value(
            {"limit": 0},
            "limit",
            default=20,
            treat_falsy_as_missing=True,
        )
        == 20
    )


def test_base_operation_wraps_action_errors_as_connector_error(connector_config):
    class FailingAction:
        def __init__(self, *_args, **_kwargs):
            pass

        def run(self):
            raise RuntimeError("boom")

    op = _NoopOperation(api_action_cls=FailingAction)

    with pytest.raises(Exception, match="Error: boom"):
        op.execute(connector_config, {"uuid": "abc"})
