from typing import Optional

from ...constants import ALERTS_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class AddCommentToAlertParams(InputModel):
    alert_uuid: str
    comment: str
    author: Optional[str] = None


class AddCommentToAlertOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = AddCommentToAlertParams

    def build_endpoint(self, parsed_input: AddCommentToAlertParams) -> str:
        return f"{ALERTS_BASE_URL}/{parsed_input.alert_uuid}/comments"

    def build_payload(self, parsed_input: AddCommentToAlertParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "author": self.payload_value(params, "author"),
            "content": self.payload_value(params, "comment"),
        }


def add_comment_to_alert(config, params: dict):
    """Add a comment to an alert."""
    return AddCommentToAlertOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
