from ...constants import CUSTOM_VERDICTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class GetCustomVerdictParams(InputModel):
    verdict_uuid: str


class GetCustomVerdictOperation(Operation):
    http_method = "GET"
    payload_parameter = None
    input_model = GetCustomVerdictParams

    def build_endpoint(self, parsed_input: GetCustomVerdictParams) -> str:
        return f"{CUSTOM_VERDICTS_V1_BASE_URL}/{parsed_input.verdict_uuid}"

    def build_payload(self, parsed_input: GetCustomVerdictParams):
        return None


def get_custom_verdict(config, params: dict):
    """Retrieve a custom verdict by UUID."""
    return GetCustomVerdictOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
