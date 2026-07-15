from typing import Optional

from ...constants import CASES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class GetCaseParams(InputModel):
    uuid: str
    community_uuid: Optional[str] = None
    render: bool = False


class GetCaseOperation(Operation):
    http_method = "get"
    payload_parameter = "params"
    input_model = GetCaseParams

    def build_endpoint(self, parsed_input: GetCaseParams) -> str:
        return f"{CASES_V1_BASE_URL}/{parsed_input.uuid}"

    def build_payload(self, parsed_input: GetCaseParams) -> dict:
        params = parsed_input.model_dump()
        payload: dict = {"render": self.payload_value(params, "render", default=False)}
        community_uuid = self.payload_value(params, "community_uuid")
        if community_uuid:
            payload["community_uuid"] = community_uuid
        return payload


def get_case(config, params: dict):
    """Retrieve a specific case."""
    return GetCaseOperation(api_action_cls=GenericAPIAction).execute(config, params)
