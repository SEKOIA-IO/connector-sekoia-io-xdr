from unittest.mock import patch

import pytest
from django.conf import settings


def test_create_content_proposal_from_pdf(connector_config, tmp_path):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        create_content_proposal_from_pdf,
    )

    pdf_file = tmp_path / "report.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%test\n")

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "data": {"content_proposal_id": "cp-pdf-001", "file_name": "report.pdf"}
        }

        result = create_content_proposal_from_pdf(
            config=connector_config,
            params={
                "file_path": str(pdf_file),
                "name": "My PDF Report",
                "source_ref": "source-pdf-001",
            },
        )

        assert action.call_count == 1
        call = action.call_args
        assert call.args[0] == connector_config
        assert call.args[1] == "POST"
        assert call.args[2] == "https://app.sekoia.io/api/v2/inthreat/reports/pdf"
        assert call.kwargs["params"] == {
            "name": "My PDF Report",
            "source_ref": "source-pdf-001",
        }
        assert "files" in call.kwargs
        assert "file" in call.kwargs["files"]
        assert result["content_proposal_id"] == "cp-pdf-001"


def test_create_content_proposal_from_pdf_accepts_file_alias(
    connector_config, tmp_path
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        create_content_proposal_from_pdf,
    )

    pdf_file = tmp_path / "report-alias.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%alias\n")

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {
            "data": {"content_proposal_id": "cp-pdf-002"}
        }

        result = create_content_proposal_from_pdf(
            config=connector_config,
            params={"file": str(pdf_file)},
        )

        assert action.call_count == 1
        assert result["content_proposal_id"] == "cp-pdf-002"


def test_create_content_proposal_from_pdf_file_not_found(connector_config):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        create_content_proposal_from_pdf,
    )

    with pytest.raises(Exception, match="PDF file not found"):
        create_content_proposal_from_pdf(
            config=connector_config,
            params={"file_path": "/tmp/does-not-exist.pdf"},
        )


def test_create_content_proposal_from_pdf_returns_raw_response(
    connector_config, tmp_path
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        create_content_proposal_from_pdf,
    )

    pdf_file = tmp_path / "report-raw.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%raw\n")

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf.GenericAPIAction"
    ) as action:
        action.return_value.run.return_value = {"status": "queued"}

        result = create_content_proposal_from_pdf(
            config=connector_config,
            params={"file_path": str(pdf_file)},
        )

        assert result == {"status": "queued"}


def test_create_content_proposal_from_pdf_wraps_api_exception(
    connector_config, tmp_path
):
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        create_content_proposal_from_pdf,
    )

    pdf_file = tmp_path / "report-error.pdf"
    pdf_file.write_bytes(b"%PDF-1.4\n%error\n")

    with patch(
        "sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf.GenericAPIAction"
    ) as action:
        action.return_value.run.side_effect = RuntimeError("upload failed")

        with pytest.raises(Exception, match="Error: upload failed"):
            create_content_proposal_from_pdf(
                config=connector_config,
                params={"file_path": str(pdf_file)},
            )


def test_create_content_proposal_from_pdf_build_payload_is_none():
    settings.configure()
    from sekoia_io_xdr.operations.ioc.create_content_proposal_from_pdf import (
        CreateContentProposalFromPdfOperation,
        CreateContentProposalFromPdfParams,
    )

    op = CreateContentProposalFromPdfOperation()
    parsed = CreateContentProposalFromPdfParams(file_path="/tmp/file.pdf")
    assert op.build_payload(parsed) is None
