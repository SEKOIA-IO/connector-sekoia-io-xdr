import json
from unittest.mock import patch

import pytest
from django.conf import settings


def test_upload_observables_with_inline_json(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.upload_observables.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "ok"}

        result = upload_observables(
            config=connector_config,
            params={
                "observables": json.dumps(
                    [
                        {"type": "domain-name", "value": "www.sekoia.io"},
                        {"type": "ipv4-addr", "value": "198.51.100.10"},
                    ]
                )
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/observables/bulk",
            json={
                "data": [
                    {"type": "domain-name", "value": "www.sekoia.io"},
                    {"type": "ipv4-addr", "value": "198.51.100.10"},
                ]
            },
        )
        assert result == {"status": "ok"}


def test_upload_observables_with_path(connector_config, tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    observables_file = tmp_path / "observables.json"
    observables_file.write_text(
        json.dumps([{"type": "url", "value": "https://example.org"}]),
        encoding="utf-8",
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.upload_observables.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "ok"}

        upload_observables(
            config=connector_config,
            params={"observables_path": str(observables_file)},
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/observables/bulk",
            json={"data": [{"type": "url", "value": "https://example.org"}]},
        )


def test_upload_observables_requires_input(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    with pytest.raises(
        Exception, match="Either observables or observables_path is required"
    ):
        upload_observables(config=connector_config, params={})


def test_upload_observables_rejects_invalid_observables_json(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    with pytest.raises(
        Exception,
        match="Expected observables to be a JSON array or object",
    ):
        upload_observables(
            config=connector_config,
            params={"observables": "{not-json}"},
        )


def test_upload_observables_rejects_missing_file(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    with pytest.raises(Exception, match="Observables file not found"):
        upload_observables(
            config=connector_config,
            params={"observables_path": "/tmp/does-not-exist-observables.json"},
        )


def test_upload_observables_accepts_dict_object(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    payload = {"type": "url", "value": "https://example.org"}
    with patch(
        "sekoia_io_xdr.operations.ioc.upload_observables.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "ok"}

        result = upload_observables(
            config=connector_config,
            params={"observables": payload},
        )

        assert action.call_args.kwargs["json"] == {"data": payload}
        assert result == {"status": "ok"}


def test_upload_observables_rejects_observables_invalid_type(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    with pytest.raises(
        Exception,
        match="Expected observables to be a JSON array or object",
    ):
        upload_observables(
            config=connector_config,
            params={"observables": 123},
        )


def test_upload_observables_rejects_invalid_json_file(connector_config, tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    observables_file = tmp_path / "observables-invalid.json"
    observables_file.write_text("{not-json}", encoding="utf-8")

    with pytest.raises(Exception, match="Observables file is not valid JSON"):
        upload_observables(
            config=connector_config,
            params={"observables_path": str(observables_file)},
        )


def test_upload_observables_blank_string_falls_back_to_path(connector_config, tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        upload_observables,
    )

    observables_file = tmp_path / "observables.json"
    observables_file.write_text(
        '[{"type": "url", "value": "https://example.org"}]', encoding="utf-8"
    )

    with patch(
        "sekoia_io_xdr.operations.ioc.upload_observables.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "ok"}

        upload_observables(
            config=connector_config,
            params={"observables": "   ", "observables_path": str(observables_file)},
        )

        assert action.call_args.kwargs["json"]["data"][0]["type"] == "url"


def test_upload_observables_build_payload_guard_without_validated_input():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import (
        UploadObservablesOperation,
        UploadObservablesParams,
    )

    op = UploadObservablesOperation()
    parsed = UploadObservablesParams.model_construct(
        observables=None,
        observables_path=None,
    )

    with pytest.raises(
        Exception, match="Either observables or observables_path is required"
    ):
        op.build_payload(parsed)


def test_upload_observables_params_accepts_none_observables_with_path(tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.upload_observables import UploadObservablesParams

    observables_file = tmp_path / "observables.json"
    observables_file.write_text("[]", encoding="utf-8")

    parsed = UploadObservablesParams(
        observables=None, observables_path=str(observables_file)
    )
    assert parsed.observables is None
