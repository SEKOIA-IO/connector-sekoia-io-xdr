from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class GetAlertParams(InputModel):
    alert_uuid: str
    include_stix: bool = False
    include_comments: bool = True
    include_history: bool = True
    include_countermeasures: bool = True
    include_cases: bool = False
    include_custom_status: bool = False


class GetAlertOperation(Operation):
    http_method = "get"
    payload_parameter = "params"
    input_model = GetAlertParams

    def build_endpoint(self, parsed_input: GetAlertParams) -> str:
        return f"{ALERTS_V1_BASE_URL}/{parsed_input.alert_uuid}"

    def build_payload(self, parsed_input: GetAlertParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "cases": self.payload_value(params, "include_cases", default=False),
            "comments": self.payload_value(params, "include_comments", default=True),
            "countermeasures": self.payload_value(
                params, "include_countermeasures", default=True
            ),
            "custom_status": self.payload_value(
                params, "include_custom_status", default=False
            ),
            "history": self.payload_value(params, "include_history", default=True),
            "stix": self.payload_value(params, "include_stix", default=False),
        }


def get_alert(config, params: dict):
    """Retrieve a specific alert."""
    return GetAlertOperation(api_action_cls=GenericAPIAction).execute(config, params)
