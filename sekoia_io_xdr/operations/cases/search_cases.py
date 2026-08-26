from ...constants import CASES_V1_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class SearchCasesParams(InputModel):
    pass


class SearchCasesOperation(Operation):
    http_method = "GET"
    payload_parameter = "params"
    input_model = SearchCasesParams

    def build_endpoint(self, parsed_input: SearchCasesParams) -> str:
        return CASES_V1_BASE_URL

    def build_payload(self, parsed_input: SearchCasesParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "date[created_at]": self.payload_value(params, "created_at"),
            "direction": self.payload_value(params, "direction"),
            "limit": self.payload_value(
                params,
                "limit",
                default=20,
                treat_falsy_as_missing=True,
            ),
            "match[assignees]": self.payload_value(params, "assignees"),
            "match[community_uuid]": self.payload_value(params, "community_uuid"),
            "match[created_by]": self.payload_value(params, "created_by"),
            "match[status_name]": self.payload_value(params, "status_name"),
            "match[status_uuid]": self.payload_value(params, "status_uuid"),
            "match[tags]": self.payload_value(params, "tags"),
            "offset": self.payload_value(
                params,
                "offset",
                default=0,
                treat_falsy_as_missing=True,
            ),
            "sort": self.payload_value(params, "sort"),
        }


def search_cases(config, params: dict):
    """Search cases filtered by optional query parameters."""
    return SearchCasesOperation(api_action_cls=GenericAPIAction).execute(config, params)
