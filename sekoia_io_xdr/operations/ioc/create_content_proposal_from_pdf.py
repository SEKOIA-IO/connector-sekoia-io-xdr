from pathlib import Path
from typing import Optional

from connectors.core.connector import ConnectorError
from pydantic import AliasChoices, Field

from ...constants import INTHREAT_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CreateContentProposalFromPdfParams(InputModel):
    file_path: str = Field(validation_alias=AliasChoices("file_path", "file"))
    name: Optional[str] = None
    source_ref: Optional[str] = None


class CreateContentProposalFromPdfOperation(Operation):
    http_method = "POST"
    payload_parameter = None
    input_model = CreateContentProposalFromPdfParams
    deprecated_parameters = {"file": "file_path"}

    def build_endpoint(self, parsed_input: CreateContentProposalFromPdfParams) -> str:
        return f"{INTHREAT_V2_BASE_URL}/reports/pdf"

    def build_payload(self, parsed_input: CreateContentProposalFromPdfParams):
        return None

    def perform(
        self,
        config: dict,
        parsed_input: CreateContentProposalFromPdfParams,
    ):
        endpoint = self.build_endpoint(parsed_input)
        query_params = {
            "name": parsed_input.name,
            "source_ref": parsed_input.source_ref,
        }
        filtered_params = {
            key: value for key, value in query_params.items() if value is not None
        }

        path = Path(parsed_input.file_path)
        if not path.exists() or not path.is_file():
            raise ConnectorError(f"PDF file not found: {parsed_input.file_path}")

        try:
            with path.open("rb") as file_handler:
                response = self.api_action_cls(
                    config,
                    self.http_method,
                    endpoint,
                    params=filtered_params,
                    files={"file": file_handler},
                ).run()
        except Exception as e:
            raise ConnectorError(f"Error: {e}") from e

        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response


def create_content_proposal_from_pdf(config, params: dict):
    """Create a content proposal from a local PDF file."""
    return CreateContentProposalFromPdfOperation(
        api_action_cls=GenericAPIAction
    ).execute(
        config,
        params,
    )
