from ...constants import CUSTOM_PRIORITIES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class GetCustomPriorityParams(InputModel):
    priority_uuid: str


class GetCustomPriorityOperation(Operation):
    http_method = "get"
    payload_parameter = None
    input_model = GetCustomPriorityParams

    def build_endpoint(self, parsed_input: GetCustomPriorityParams) -> str:
        return f"{CUSTOM_PRIORITIES_V1_BASE_URL}/{parsed_input.priority_uuid}"

    def build_payload(self, parsed_input: GetCustomPriorityParams):
        return None


def get_custom_priority(config, params: dict):
    """Retrieve a custom priority by UUID."""
    return GetCustomPriorityOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
