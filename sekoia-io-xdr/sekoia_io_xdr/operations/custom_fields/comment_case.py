from pydantic import AliasChoices, Field

from ...constants import CASES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class CommentCaseParams(InputModel):
    uuid: str = Field(validation_alias=AliasChoices("uuid", "case_uuid"))
    content: str


class CommentCaseOperation(Operation):
    http_method = "POST"
    payload_parameter = "json"
    input_model = CommentCaseParams

    def build_endpoint(self, parsed_input: CommentCaseParams) -> str:
        return f"{CASES_V1_BASE_URL}/{parsed_input.uuid}/comments"

    def build_payload(self, parsed_input: CommentCaseParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "content": self.payload_value(params, "content"),
        }


def comment_case(config, params: dict):
    """Create a new comment on a case."""
    return CommentCaseOperation(api_action_cls=GenericAPIAction).execute(config, params)
