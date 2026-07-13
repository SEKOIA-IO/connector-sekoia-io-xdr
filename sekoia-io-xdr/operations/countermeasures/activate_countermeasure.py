from typing import Optional

from ...constants import ALERTS_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class ActivateCountermeasureParams(InputModel):
    countermeasure_uuid: str
    content: str
    author: Optional[str] = None


class ActivateCountermeasureOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = ActivateCountermeasureParams

    def build_endpoint(self, parsed_input: ActivateCountermeasureParams) -> str:
        return f"{ALERTS_BASE_URL}/countermeasures/{parsed_input.countermeasure_uuid}/activate"

    def build_payload(self, parsed_input: ActivateCountermeasureParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "comment": {
                "content": self.payload_value(params, "content"),
                "author": self.payload_value(params, "author"),
            }
        }


def activate_countermeasure(config, params):
    """Activate a countermeasure."""
    return ActivateCountermeasureOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
