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
