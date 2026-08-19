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
