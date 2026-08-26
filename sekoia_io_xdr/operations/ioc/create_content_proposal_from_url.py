from typing import Optional

from connectors.core.connector import ConnectorError

from ...constants import INTHREAT_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CreateContentProposalFromUrlParams(InputModel):
    url: str
    source_ref: Optional[str] = None


class CreateContentProposalFromUrlOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = CreateContentProposalFromUrlParams

    def build_endpoint(self, parsed_input: CreateContentProposalFromUrlParams) -> str:
        return f"{INTHREAT_V2_BASE_URL}/reports/url"

    def build_payload(self, parsed_input: CreateContentProposalFromUrlParams) -> dict:
        return {"url": parsed_input.url}

    def perform(
        self,
        config: dict,
        parsed_input: CreateContentProposalFromUrlParams,
    ):
        endpoint = self.build_endpoint(parsed_input)
        payload = self.build_payload(parsed_input)
        query_params = {"source_ref": parsed_input.source_ref}
        filtered_params = {
            key: value for key, value in query_params.items() if value is not None
        }

        try:
            response = self.api_action_cls(
                config,
                self.http_method,
                endpoint,
                params=filtered_params,
                json=payload,
            ).run()
        except Exception as e:
            raise ConnectorError(f"Error: {e}") from e

        if isinstance(response, dict) and "data" in response:
            return response["data"]
        return response


def create_content_proposal_from_url(config, params: dict):
    """Create a content proposal from a report URL."""
    return CreateContentProposalFromUrlOperation(
        api_action_cls=GenericAPIAction
    ).execute(
        config,
        params,
    )
