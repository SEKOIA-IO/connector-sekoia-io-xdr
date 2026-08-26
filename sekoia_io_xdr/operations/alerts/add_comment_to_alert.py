from typing import Optional

from pydantic import AliasChoices, Field

from ...constants import ALERTS_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class AddCommentToAlertParams(InputModel):
    uuid: str = Field(validation_alias=AliasChoices("uuid", "alert_uuid"))
    content: str = Field(validation_alias=AliasChoices("content", "comment"))
    author: Optional[str] = None


class AddCommentToAlertOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = AddCommentToAlertParams
    deprecated_aliases = DeprecatedAliases(
        single={
            "uuid": "alert_uuid",
            "content": "comment",
        }
    )

    def build_endpoint(self, parsed_input: AddCommentToAlertParams) -> str:
        return f"{ALERTS_V1_BASE_URL}/{parsed_input.uuid}/comments"

    def build_payload(self, parsed_input: AddCommentToAlertParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "author": self.payload_value(params, "author"),
            "content": self.payload_value(params, "content"),
        }


def add_comment_to_alert(config, params: dict):
    """Add a comment to an alert."""
    return AddCommentToAlertOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
