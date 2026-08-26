from ...constants import ASSETS_V2_BASE_URL
from ...utils import GenericAPIAction
from ..base import InputModel, Operation


class ListAssetsParams(InputModel):
    pass


class ListAssetsOperation(Operation):
    http_method = "GET"
    payload_parameter = "params"
    input_model = ListAssetsParams

    def build_endpoint(self, parsed_input: ListAssetsParams) -> str:
        return ASSETS_V2_BASE_URL

    def build_payload(self, parsed_input: ListAssetsParams) -> dict:
        params = parsed_input.model_dump()
        return {
            "also_search_in_detection_properties": self.payload_value(
                params, "also_search_in_detection_properties", default=False
            ),
            "also_search_in_tags": self.payload_value(
                params, "also_search_in_tags", default=False
            ),
            "category": self.payload_value(params, "category"),
            "community_uuids": self.payload_value(params, "community_uuids"),
            "connectors": self.payload_value(params, "connectors"),
            "connectors_configuration": self.payload_value(
                params, "connectors_configuration"
            ),
            "criticality": self.payload_value(params, "criticality"),
            "direction": self.payload_value(params, "direction"),
            "format": self.payload_value(params, "format"),
            "include_intake_formats": self.payload_value(
                params, "include_intake_formats", default=False
            ),
            "include_revoked": self.payload_value(
                params, "include_revoked", default=False
            ),
            "incorporate_atoms": self.payload_value(
                params, "incorporate_atoms", default=False
            ),
            "intake_format_uuids": self.payload_value(params, "intake_format_uuids"),
            "limit": self.payload_value(
                params,
                "limit",
                default=20,
                treat_falsy_as_missing=True,
            ),
            "offset": self.payload_value(
                params,
                "offset",
                default=0,
                treat_falsy_as_missing=True,
            ),
            "reviewed": self.payload_value(params, "reviewed"),
            "rule_uuid": self.payload_value(params, "rule_uuid"),
            "rule_version": self.payload_value(params, "rule_version"),
            "search": self.payload_value(params, "search"),
            "sort": self.payload_value(params, "sort"),
            "source": self.payload_value(params, "source"),
            "tags": self.payload_value(params, "tags"),
            "type": self.payload_value(params, "type"),
            "uuids": self.payload_value(params, "uuids"),
            "with_telemetry": self.payload_value(
                params, "with_telemetry", default=False
            ),
        }


def list_assets(config, params: dict):
    """Search assets filtered by optional query parameters."""
    return ListAssetsOperation(api_action_cls=GenericAPIAction).execute(config, params)
