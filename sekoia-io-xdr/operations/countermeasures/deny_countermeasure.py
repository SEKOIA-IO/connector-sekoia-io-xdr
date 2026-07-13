from typing import Optional

from ...constants import ALERTS_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class DenyCountermeasureParams(InputModel):
    countermeasure_uuid: str
    content: str
    author: Optional[str] = None


class DenyCountermeasureOperation(Operation):
    http_method = "PATCH"
    payload_parameter = "json"
    input_model = DenyCountermeasureParams

    def build_endpoint(self, parsed_input: DenyCountermeasureParams) -> str:
        return (
            f"{ALERTS_BASE_URL}/countermeasures/{parsed_input.countermeasure_uuid}/deny"
        )

    def build_payload(self, parsed_input: DenyCountermeasureParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "comment": {
                "content": self.payload_value(params, "content"),
                "author": self.payload_value(params, "author"),
            }
        }


def deny_countermeasure(config, params):
    """Deny a countermeasure."""
    return DenyCountermeasureOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
