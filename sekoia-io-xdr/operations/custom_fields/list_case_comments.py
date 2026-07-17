from pydantic import AliasChoices, Field

from ...constants import CASES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import DeprecatedAliases, InputModel, Operation


class ListCaseCommentsParams(InputModel):
    case_uuid: str = Field(validation_alias=AliasChoices("case_uuid", "uuid"))


class ListCaseCommentsOperation(Operation):
    http_method = "GET"
    payload_parameter = "params"
    input_model = ListCaseCommentsParams
    deprecated_aliases = DeprecatedAliases(single={"case_uuid": "uuid"})

    def build_endpoint(self, parsed_input: ListCaseCommentsParams) -> str:
        return f"{CASES_V1_BASE_URL}/{parsed_input.case_uuid}/comments"

    def build_payload(self, parsed_input: ListCaseCommentsParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "date[created_at]": self.payload_value(params, "date[created_at]"),
            "direction": self.payload_value(params, "direction"),
            "limit": self.payload_value(params, "limit", default=20),
            "match[created_by]": self.payload_value(params, "match[created_by]"),
            "offset": self.payload_value(params, "offset", default=0),
            "sort": self.payload_value(params, "sort"),
        }


def list_case_comments(config, params: dict):
    """List all comments of a case."""
    return ListCaseCommentsOperation(api_action_cls=GenericAPIAction).execute(
        config, params
    )
