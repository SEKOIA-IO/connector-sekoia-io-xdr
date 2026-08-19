import json
from unittest.mock import patch

import pytest
from django.conf import settings


def test_create_content_proposal_with_inline_bundle(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle = {
        "type": "bundle",
        "id": "bundle--11111111-1111-1111-1111-111111111111",
        "objects": [{"type": "indicator", "id": "indicator--1"}],
    }

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "data": {
                "content_proposal_id": "cp-0001",
                "file_name": "proposal.stix.json",
            }
        }

        result = create_content_proposal(
            config=connector_config,
            params={
                "bundle": json.dumps(bundle),
                "auto_merge": True,
                "enrich": False,
                "name": "IOC proposal",
                "assigned_to": "avatar-uuid-001",
            },
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/bundles",
            params={
                "auto_merge": True,
                "enrich": False,
                "name": "IOC proposal",
                "assigned_to": "avatar-uuid-001",
            },
            json={"data": bundle},
        )
        assert result == {
            "content_proposal_id": "cp-0001",
            "file_name": "proposal.stix.json",
        }


def test_create_content_proposal_with_bundle_path(connector_config, tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle = {
        "type": "bundle",
        "id": "bundle--22222222-2222-2222-2222-222222222222",
        "objects": [{"type": "indicator", "id": "indicator--2"}],
    }
    bundle_file = tmp_path / "bundle.json"
    bundle_file.write_text(json.dumps(bundle), encoding="utf-8")

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "data": {"content_proposal_id": "cp-0002"}
        }

        result = create_content_proposal(
            config=connector_config,
            params={"bundle_path": str(bundle_file)},
        )

        action.assert_called_once_with(
            connector_config,
            "POST",
            "https://app.sekoia.io/api/v2/inthreat/bundles",
            params={
                "auto_merge": False,
                "enrich": True,
            },
            json={"data": bundle},
        )
        assert result == {"content_proposal_id": "cp-0002"}


def test_create_content_proposal_requires_bundle_input(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    with pytest.raises(Exception, match="Either bundle or bundle_path is required"):
        create_content_proposal(config=connector_config, params={})


def test_create_content_proposal_rejects_non_object_bundle_json(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    with pytest.raises(Exception, match="Expected bundle to be a JSON object"):
        create_content_proposal(
            config=connector_config,
            params={"bundle": "[1, 2, 3]"},
        )


def test_create_content_proposal_rejects_missing_bundle_file(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    with pytest.raises(Exception, match="Bundle file not found"):
        create_content_proposal(
            config=connector_config,
            params={"bundle_path": "/tmp/does-not-exist-bundle.json"},
        )


def test_create_content_proposal_returns_raw_response_when_no_data_key(
    connector_config,
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle = {
        "type": "bundle",
        "id": "bundle--33333333-3333-3333-3333-333333333333",
        "objects": [],
    }

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "queued"}

        result = create_content_proposal(
            config=connector_config,
            params={"bundle": json.dumps(bundle)},
        )

        assert result == {"status": "queued"}


def test_create_content_proposal_rejects_invalid_bundle_type(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    with pytest.raises(Exception, match="Expected bundle to be a JSON object"):
        create_content_proposal(
            config=connector_config,
            params={"bundle": 123},
        )


def test_create_content_proposal_rejects_invalid_bundle_file_json(
    connector_config, tmp_path
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle_file = tmp_path / "bundle-invalid.json"
    bundle_file.write_text("{not-json}", encoding="utf-8")

    with pytest.raises(Exception, match="Bundle file is not valid JSON"):
        create_content_proposal(
            config=connector_config,
            params={"bundle_path": str(bundle_file)},
        )


def test_create_content_proposal_rejects_bundle_file_non_object(
    connector_config, tmp_path
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle_file = tmp_path / "bundle-list.json"
    bundle_file.write_text("[]", encoding="utf-8")

    with pytest.raises(Exception, match="Bundle file must contain a JSON object"):
        create_content_proposal(
            config=connector_config,
            params={"bundle_path": str(bundle_file)},
        )


def test_create_content_proposal_wraps_api_exception(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        create_content_proposal,
    )

    bundle = {
        "type": "bundle",
        "id": "bundle--44444444-4444-4444-4444-444444444444",
        "objects": [],
    }

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal.GenericAPIAction"
    ) as action:
        action.return_value.run.side_effect = RuntimeError("api failed")

        with pytest.raises(Exception, match="Error: api failed"):
            create_content_proposal(
                config=connector_config,
                params={"bundle": json.dumps(bundle)},
            )


def test_create_content_proposal_params_accepts_bundle_dict():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        CreateContentProposalParams,
    )

    parsed = CreateContentProposalParams(
        bundle={"type": "bundle", "id": "bundle--1", "objects": []}
    )
    assert parsed.bundle["type"] == "bundle"


def test_create_content_proposal_params_rejects_invalid_bundle_json_string():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        CreateContentProposalParams,
    )

    with pytest.raises(Exception, match="Expected bundle to be a JSON object"):
        CreateContentProposalParams(bundle="{not-json}")


def test_create_content_proposal_build_payload_guard_without_validated_input():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        CreateContentProposalOperation,
        CreateContentProposalParams,
    )

    op = CreateContentProposalOperation()
    parsed = CreateContentProposalParams.model_construct(bundle=None, bundle_path=None)

    with pytest.raises(Exception, match="Either bundle or bundle_path is required"):
        op.build_payload(parsed)


def test_create_content_proposal_params_empty_bundle_string_becomes_none_with_path(
    tmp_path,
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        CreateContentProposalParams,
    )

    bundle_file = tmp_path / "bundle.json"
    bundle_file.write_text(
        '{"type": "bundle", "id": "bundle--x", "objects": []}', encoding="utf-8"
    )

    parsed = CreateContentProposalParams(bundle="   ", bundle_path=str(bundle_file))
    assert parsed.bundle is None
    assert parsed.bundle_path == str(bundle_file)


def test_create_content_proposal_params_accepts_bundle_none_with_path(tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal import (
        CreateContentProposalParams,
    )

    bundle_file = tmp_path / "bundle.json"
    bundle_file.write_text(
        '{"type": "bundle", "id": "bundle--x", "objects": []}', encoding="utf-8"
    )

    parsed = CreateContentProposalParams(bundle=None, bundle_path=str(bundle_file))
    assert parsed.bundle is None
