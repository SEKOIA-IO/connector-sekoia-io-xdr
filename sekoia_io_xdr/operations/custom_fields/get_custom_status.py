from ...constants import CUSTOM_STATUSES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class GetCustomStatusParams(InputModel):
    status_uuid: str


class GetCustomStatusOperation(Operation):
    http_method = "GET"
    payload_parameter = None
    input_model = GetCustomStatusParams

    def build_endpoint(self, parsed_input: GetCustomStatusParams) -> str:
        return f"{CUSTOM_STATUSES_V1_BASE_URL}/{parsed_input.status_uuid}"

    def build_payload(self, parsed_input: GetCustomStatusParams):
        return None


def get_custom_status(config, params: dict):
    """Retrieve a custom status by UUID."""
    return GetCustomStatusOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
